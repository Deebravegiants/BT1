# [H] CVE-2024-46898

## Summary
Severity: High
Advisory: CVE-2024-46898
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-46898
Type: osv

## Details
SHIRASAGI prior to v1.19.1 processes URLs in HTTP requests improperly, resulting in a path traversal vulnerability. If this vulnerability is exploited, arbitrary files on the server may be retrieved when processing crafted HTTP requests.

## References
- https://jvn.jp/en/jp/JVN58721679/
- https://www.ss-proj.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46898.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46898
- https://github.com/shirasagi/shirasagi/commit/5ac4685d7e4330f949f13219069107fc5d768934
