# [H] ZimaOS Arbitrary File Read via Parameter Manipulation

## Summary
Severity: High
Advisory: CVE-2024-48931
Aliases: GHSA-hjw2-9gq5-qgwj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-48931
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.2.4 and all prior versions, the ZimaOS API endpoint `http://<Zima_Server_IP:PORT>/v3/file?token=<token>&files=<file_path>` is vulnerable to arbitrary file reading due to improper input validation. By manipulating the `files` parameter, authenticated users can read sensitive system files, including `/etc/shadow`, which contains password hashes for all users. This vulnerability exposes critical system data and poses a high risk for privilege escalation or system compromise. The vulnerability occurs because the API endpoint does not validate or restrict file paths provided via the `files` parameter. An attacker can exploit this by manipulating the file path to access sensitive files outside the intended directory. As of time of publication, no known patched versions are available.

## References
- https://youtu.be/FyIfcmCyDXs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48931.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-hjw2-9gq5-qgwj
- https://nvd.nist.gov/vuln/detail/CVE-2024-48931
