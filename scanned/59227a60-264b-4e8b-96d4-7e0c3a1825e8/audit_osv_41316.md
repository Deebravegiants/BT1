# [M] SMB minimum protocol dialect defaults to SMB1

## Summary
Severity: Medium
Advisory: CVE-2026-59293
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59293
Type: osv

## Details
Unless the application explicitly raises smbMinVersion, the jCIFS client will negotiate down to SMB1/CIFS, which lacks mandatory signing/encryption and is vulnerable to NTLM relay and content-tampering MITM.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12

## References
- https://spring.io/security/cve-2026-59293
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59293.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59293
