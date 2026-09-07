# [M] Open WebUI Allows Arbitrary File Write via the `/models/upload` Endpoint

## Summary
Severity: Medium
Advisory: GHSA-crh6-pj8c-xrhc
CVE: CVE-2024-7034
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-crh6-pj8c-xrhc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In open-webui version 0.3.8, the endpoint `/models/upload` is vulnerable to arbitrary file write due to improper handling of user-supplied filenames. The vulnerability arises from the usage of `file_path = f"{UPLOAD_DIR}/{file.filename}"` without proper input validation or sanitization. An attacker can exploit this by manipulating the `file.filename` parameter to include directory traversal sequences, causing the resulting `file_path` to escape the intended `UPLOAD_DIR` and potentially overwrite arbitrary files on the system. This can lead to unauthorized modifications of system binaries, configuration files, or sensitive data, potentially enabling remote command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7034
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/711beada-10fe-4567-9278-80a689da8613
