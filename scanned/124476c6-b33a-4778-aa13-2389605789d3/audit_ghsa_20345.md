# [H] Jupyter server Token bruteforcing

## Summary
Severity: High
Advisory: GHSA-q874-g24w-4q9g
CVE: CVE-2022-29241
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-q874-g24w-4q9g
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <1.17.1
- PyPI: `jupyter-server` — affected >=2.0.0a0 <2.0.0a1

## Details
Affects: Notebook and Lab between 6.4.0?(potentially earlier) and 6.4.11 (currently latest). Jupyter Server <=1.16.0. If I am correct about the responsible code it will affect Jupyter-Server 1.17.0 and 2.0.0a0 as well.
Description: If notebook server is started with a value of `root_dir` that contains the starting user's home directory, then the underlying REST API can be used to leak the access token assigned at start time by guessing/brute forcing the PID of the jupyter server. While this requires an authenticated user session, this url can be used from an xss payload (as in CVE-2021-32798) or from a hooked or otherwise compromised browser to leak this access token to a malicious third party. This token can be used along with the REST API to interact with Jupyter services/notebooks such as modifying or overwriting critical files, such as .bashrc or .ssh/authorized_keys, allowing a malicious user to read potentially sensitive data and possibly gain control of the impacted system.

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-q874-g24w-4q9g
- https://nvd.nist.gov/vuln/detail/CVE-2022-29241
- https://github.com/jupyter-server/jupyter_server/commit/3485007abbb459585357212dcaa20521989272e8
- https://github.com/jupyter-server/jupyter_server/commit/877da10cd0d7ae45f8b1e385fa1f5a335e7adf1f
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2022-211.yaml
