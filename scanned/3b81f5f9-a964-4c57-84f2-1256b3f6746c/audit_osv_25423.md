# [C] CVE-2023-36328

## Summary
Severity: Critical
Advisory: CVE-2023-36328
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-01
Source: https://osv.dev/vulnerability/CVE-2023-36328
Type: osv

## Details
Integer Overflow vulnerability in mp_grow in libtom libtommath before commit beba892bc0d4e4ded4d667ab1d2a94f4d75109a9, allows attackers to execute arbitrary code and cause a denial of service (DoS).

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00011.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36328.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3H2PFUTBKQUDSOJXQQS7LUSZQWT3JTW2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/46GORAXZ34MHQNUGJBKS7PJ5NSMIAJGC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6ZUPWZGPFJ4JOI2NIP7YLRKZD5YXQTBK/
- https://nvd.nist.gov/vuln/detail/CVE-2023-36328
- https://github.com/libtom/libtommath/pull/546
