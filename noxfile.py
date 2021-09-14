"""Nox sessions."""

import tempfile
from pathlib import Path

import nox

package = "demo_python_project_backstage"
nox.options.sessions = "lint", "safety", "tests"
locations = "src", "tests", "noxfile.py"


def install_with_constraints(session, *args, **kwargs):
    """Install packages constrained by Poetry's lock file."""
    requirements = tempfile.NamedTemporaryFile(delete=False)
    try:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
    finally:
        requirements.close()
        Path(requirements.name).unlink()


@nox.session
def black(session):
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session
def lint(session):
    """Lint using flake8 and isort."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "isort",
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-comprehensions",
        "flake8-docstrings",
        "pep8-naming",
    )
    session.run("isort", "--check", "--diff", "--profile", "black", *args)
    session.run("flake8", *args)


@nox.session
def publish_docs(session):
    """Publish documentation to GitHub Pages."""
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--requirement={requirements.name}")
    Path(requirements.name).unlink()
    session.run("mkdocs", "gh-deploy")


@nox.session
def serve_docs(session):
    """Build and serve documentation locally."""
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--requirement={requirements.name}")
    Path(requirements.name).unlink()
    session.run("mkdocs", "serve")


@nox.session
def safety(session):
    """Scan dependencies for insecure packages."""
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
    Path(requirements.name).unlink()


@nox.session
def tests(session):
    """Run the unit tests."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)


@nox.session
def xdoctest(session):
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "xdoctest[all]")
    session.run("python", "-m", "xdoctest", package, *args)
