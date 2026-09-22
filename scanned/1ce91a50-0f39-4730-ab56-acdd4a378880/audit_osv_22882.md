# [M] Stack Buffer Overflow in Jettison

## Summary
Severity: Medium
Advisory: CVE-2022-40149
Aliases: GHSA-56h3-78gp-v83r
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-16
Source: https://osv.dev/vulnerability/CVE-2022-40149
Type: osv

## Details
Those using Jettison to parse untrusted XML or JSON data may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow. This effect may support a denial of service attack.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=46538
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40149.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40149
- https://www.debian.org/security/2023/dsa-5312
- https://github.com/jettison-json/jettison/issues/45
- https://lists.debian.org/debian-lts-announce/2022/11/msg00011.html
