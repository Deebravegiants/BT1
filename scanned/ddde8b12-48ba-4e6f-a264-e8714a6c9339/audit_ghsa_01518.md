# [H] Log injection in uvicorn

## Summary
Severity: High
Advisory: GHSA-33c7-2mpw-hg34
CVE: CVE-2020-7694
CWE: CWE-116, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-33c7-2mpw-hg34
Type: github-advisory

## Affected
- PyPI: `uvicorn` — affected >=0 <0.11.7

## Details
This affects all versions of package uvicorn. The request logger provided by the package is vulnerable to ASNI escape sequence injection. Whenever any HTTP request is received, the default behaviour of uvicorn is to log its details to either the console or a log file. When attackers request crafted URLs with percent-encoded escape sequences, the logging component will log the URL after it's been processed with urllib.parse.unquote, therefore converting any percent-encoded characters into their single-character equivalent, which can have special meaning in terminal emulators. By requesting URLs with crafted paths, attackers can: * Pollute uvicorn's access logs, therefore jeopardising the integrity of such files. * Use ANSI sequence codes to attempt to interact with the terminal emulator that's displaying the logs (either in real time or from a file).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7694
- https://github.com/encode/uvicorn/issues/723
- https://github.com/encode/uvicorn/commit/895807f94ea9a8e588605c12076b7d7517cda503
- https://github.com/encode/uvicorn
- https://github.com/pypa/advisory-database/tree/main/vulns/uvicorn/PYSEC-2020-150.yaml
- https://snyk.io/vuln/SNYK-PYTHON-UVICORN-575560
