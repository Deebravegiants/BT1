# [C] Malware in ctx

## Summary
Severity: Critical
Advisory: GHSA-4g82-3jcr-q52w
CWE: CWE-912
Ecosystem: PyPI
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-4g82-3jcr-q52w
Type: github-advisory

## Affected
- PyPI: `ctx` — affected >=0

## Details
The `ctx` hosted project on [PyPI](https://pypi.org/project/ctx/) was taken over via user account compromise and replaced with a malicious project which contained runtime code that collected the content of `os.environ.items()` when instantiating `Ctx` objects. The captured environment variables were sent as a base64 encoded query parameter to a heroku application running at `https://anti-theft-web.herokuapp.com`.

If you installed the package between May 14, 2022 and May 24, 2022, and your environment variables contain sensitive data like passwords and API keys (like `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`), we advise you to rotate your passwords and keys, then perform an audit to determine if they were exploited.

## References
- https://github.com/figlief/ctx
- https://isc.sans.edu/forums/diary/ctx+Python+Library+Updated+with+Extra+Features/28678
- https://portswigger.net/daily-swig/malicious-python-library-ctx-removed-from-pypi-repo
- https://python-security.readthedocs.io/pypi-vuln/index-2022-05-24-ctx-domain-takeover.html
