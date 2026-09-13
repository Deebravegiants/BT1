# [H] CVE-2022-27781

## Summary
Severity: High
Advisory: CVE-2022-27781
Aliases: CURL-CVE-2022-27781
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-27781
Type: osv

## Details
libcurl provides the `CURLOPT_CERTINFO` option to allow applications torequest details to be returned about a server's certificate chain.Due to an erroneous function, a malicious server could make libcurl built withNSS get stuck in a never-ending busy-loop when trying to retrieve thatinformation.

## References
- https://hackerone.com/reports/1555441
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/27xxx/CVE-2022-27781.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-27781
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0009/
- https://www.debian.org/security/2022/dsa-5197
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
