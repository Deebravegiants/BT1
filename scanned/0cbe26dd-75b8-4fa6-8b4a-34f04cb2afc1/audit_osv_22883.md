# [M] Stack Buffer Overflow in xstream

## Summary
Severity: Medium
Advisory: CVE-2022-40151
Aliases: GHSA-f8cc-g7j8-xxpm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-16
Source: https://osv.dev/vulnerability/CVE-2022-40151
Type: osv

## Details
Those using Xstream to seralize XML data may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow. This effect may support a denial of service attack.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=47367
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40151.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40151
- https://github.com/x-stream/xstream/issues/304
