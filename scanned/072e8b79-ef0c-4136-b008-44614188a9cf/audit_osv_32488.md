# [M] CVE-2025-30742

## Summary
Severity: Medium
Advisory: CVE-2025-30742
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-03-26
Source: https://osv.dev/vulnerability/CVE-2025-30742
Type: osv

## Details
httpd.c in atophttpd 2.8.0 has an off-by-one error and resultant out-of-bounds read because a certain 1024-character req string would not have a final '\0' character.

## References
- https://github.com/pizhenwei/atophttpd/blob/74c9f14796b15dc9de5839a5749202f933937a9c/httpd.c#L376-L381
- https://github.com/pizhenwei/atophttpd/blob/74c9f14796b15dc9de5839a5749202f933937a9c/httpd.c#L492-L496
- https://github.com/pizhenwei/atophttpd/blob/74c9f14796b15dc9de5839a5749202f933937a9c/httpd.c#L71-L72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30742.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30742
