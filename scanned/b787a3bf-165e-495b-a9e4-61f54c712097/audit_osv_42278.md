# [H] Apache Neethi: Remote PolicyReference fetch lacks resource bounds

## Summary
Severity: High
Advisory: CVE-2026-66144
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66144
Type: osv

## Details
Although remote policy references are not retrieved during policy normalization, if they are manually retrieved via the API it can cause a denial of service attack if a huge policy is retrieved. Users are recommended to upgrade to version 3.2.3, which fixes this issue by imposing a default maximum size on data read from remote policy references.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/10
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66144.json
- https://lists.apache.org/thread/80xwwbhkqvbwkkmco6yl6fr5xkpdysjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-66144
