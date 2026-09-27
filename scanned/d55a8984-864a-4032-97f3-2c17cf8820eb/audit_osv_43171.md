# [H] OpenSignLabs opensignserver - Missing Authentication for Critical Function

## Summary
Severity: High
Advisory: CVE-2026-72688
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72688
Type: osv

## Details
A missing authentication vulnerability in OpenSignLabs opensignserver through 2.37.0 allows an unauthenticated remote attacker to read arbitrary stored documents via the fileupload Parse cloud function. The function mints MASTER_KEY-signed file access tokens for any caller-supplied URL without performing any session check, defeating the only access control protecting stored contract files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72688.json
- https://github.com/OpenSignLabs/OpenSign
- https://nvd.nist.gov/vuln/detail/CVE-2026-72688
