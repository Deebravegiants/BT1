# [H] Kedro allows Remote Code Execution by Pulling Micro Packages

## Summary
Severity: High
Advisory: GHSA-rm69-wvpv-r2w7
CVE: CVE-2024-12215
CWE: CWE-20, CWE-829, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-rm69-wvpv-r2w7
Type: github-advisory

## Affected
- PyPI: `kedro` — affected >=0

## Details
In kedro-org/kedro version 0.19.8, the `pull_package()` API function allows users to download and extract micro packages from the Internet. However, the function `project_wheel_metadata()` within the code path can execute the `setup.py` file inside the tar file, leading to remote code execution (RCE) by running arbitrary commands on the victim's machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12215
- https://github.com/kedro-org/kedro
- https://huntr.com/bounties/fad27503-97a4-4933-91d4-96223b8c54d8
