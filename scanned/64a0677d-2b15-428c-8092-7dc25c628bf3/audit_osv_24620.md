# [H] CVE-2023-24042

## Summary
Severity: High
Advisory: CVE-2023-24042
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-21
Source: https://osv.dev/vulnerability/CVE-2023-24042
Type: osv

## Details
A race condition in LightFTP through 2.2 allows an attacker to achieve path traversal via a malformed FTP request. A handler thread can use an overwritten context->FileName.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24042.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24042
- https://github.com/hfiref0x/LightFTP/issues/25
