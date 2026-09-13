# [H] AstrBot contains a directory traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-xrj9-mw57-j34v
CVE: CVE-2025-57698
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-07
Source: https://github.com/advisories/GHSA-xrj9-mw57-j34v
Type: github-advisory

## Affected
- PyPI: `AstrBot` — affected >=0

## Details
AstrBot Project v3.5.22 contains a directory traversal vulnerability. The handler function install_plugin_upload of the interface '/plugin/install-upload' parses the filename from the request body provided by the user, and directly uses the filename to assign to file_path without checking the validity of the filename. The variable file_path is then passed as a parameter to the function `file.save`, so that the file in the request body can be saved to any location in the file system through directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57698
- https://github.com/AstrBotDevs/AstrBot
- https://github.com/DYX217/vulnerability-explore/blob/main/2/README.md
