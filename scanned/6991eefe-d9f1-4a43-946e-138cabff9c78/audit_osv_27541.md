# [C] Arbitrary Upload & Read via Path Traversal in parisneo/lollms-webui

## Summary
Severity: Critical
Advisory: CVE-2024-2361
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2024-2361
Type: osv

## Details
A vulnerability in the parisneo/lollms-webui allows for arbitrary file upload and read due to insufficient sanitization of user-supplied input. Specifically, the issue resides in the `install_model()` function within `lollms_core/lollms/binding.py`, where the application fails to properly sanitize the `file://` protocol and other inputs, leading to arbitrary read and upload capabilities. Attackers can exploit this vulnerability by manipulating the `path` and `variant_name` parameters to achieve path traversal, allowing for the reading of arbitrary files and uploading files to arbitrary locations on the server. This vulnerability affects the latest version of parisneo/lollms-webui.

## References
- https://huntr.com/bounties/cd383817-924a-445a-838e-d0c867c6a176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2361.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2361
