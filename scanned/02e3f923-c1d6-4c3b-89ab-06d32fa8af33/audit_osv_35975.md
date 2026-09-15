# [M] Velociraptor NETWORK ACL bypass via upload_azure / upload_sftp / upload_smb VQL plugins

## Summary
Severity: Medium
Advisory: CVE-2026-18348
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18348
Type: osv

## Details
Missing authorization check in the upload_azure, upload_sftp, and upload_smb VQL plugins allows an authenticated analyst-role user can initiate attacker-controlled outbound network connections from the Velociraptor server, bypassing the NETWORK ACL permission boundary. This enables internal network reconnaissance via port oracle and potential data exfiltration to external endpoints.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18348/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18348.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18348
- https://github.com/Velocidex/velociraptor/commit/48824fb51a2bdba832abc281e719ecbed74736df
