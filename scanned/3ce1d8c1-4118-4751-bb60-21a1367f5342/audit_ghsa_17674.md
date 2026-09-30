# [H] Jupyter Core on Windows Has Uncontrolled Search Path Element Local Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-33p9-3p43-82vq
CVE: CVE-2025-30167
CWE: CWE-427
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-33p9-3p43-82vq
Type: github-advisory

## Affected
- PyPI: `jupyter_core` — affected >=0 <5.8.1

## Details
## Impact

On Windows, the shared `%PROGRAMDATA%` directory is searched for configuration files (`SYSTEM_CONFIG_PATH` and `SYSTEM_JUPYTER_PATH`), which may allow users to create configuration files affecting other users.

Only shared Windows systems with multiple users and unprotected `%PROGRAMDATA%` are affected.

## Mitigations

- upgrade to `jupyter_core>=5.8.1` (5.8.0 is patched but breaks `jupyter-server`) , or
- as administrator, modify the permissions on the `%PROGRAMDATA%` directory so it is not writable by unauthorized users, or
- as administrator, create the `%PROGRAMDATA%\jupyter` directory with appropriately restrictive permissions, or
- as user or administrator, set the `%PROGRAMDATA%` environment variable to a directory with appropriately restrictive permissions (e.g. controlled by administrators _or_ the current user)

## Credit

Reported via Trend Micro Zero Day Initiative as ZDI-CAN-25932

## References
- https://github.com/jupyter/jupyter_core/security/advisories/GHSA-33p9-3p43-82vq
- https://nvd.nist.gov/vuln/detail/CVE-2025-30167
- https://github.com/jupyter/jupyter_core/commit/5e8965600adda6b416692ce7e85ecb2bd814bd52
- https://github.com/jupyter/jupyter_core
