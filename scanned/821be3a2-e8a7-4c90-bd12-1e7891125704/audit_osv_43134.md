# [M] Windmill Labs Windmill - Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-72539
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72539
Type: osv

## Details
An information disclosure vulnerability in Windmill Labs Windmill through 1.783.0 allows any authenticated workspace member to read legacy ownerless draft scripts that contain plaintext resource credentials. Drafts with a null owner email bypass ACL enforcement and are returned to any workspace member who queries the drafts endpoint. Sensitive credentials stored in these drafts are exposed across ACL boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72539.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72539
- https://github.com/windmill-labs/windmill
