# [M] CVE-2022-32205

## Summary
Severity: Medium
Advisory: CVE-2022-32205
Aliases: CURL-CVE-2022-32205
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2022-07-07
Source: https://osv.dev/vulnerability/CVE-2022-32205
Type: osv

## Details
A malicious server can serve excessive amounts of `Set-Cookie:` headers in a HTTP response to curl and curl < 7.84.0 stores all of them. A sufficiently large amount of (big) cookies make subsequent HTTP requests to this, or other servers to which the cookies match, create requests that become larger than the threshold that curl uses internally to avoid sending crazy large requests (1048576 bytes) and instead returns an error.This denial state might remain for as long as the same cookies are kept, match and haven't expired. Due to cookie matching rules, a server on `foo.example.com` can set cookies that also would match for `bar.example.com`, making it it possible for a "sister server" to effectively cause a denial of service for a sibling site on the same second level domain using this method.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-333517.pdf
- https://hackerone.com/reports/1569946
- https://support.apple.com/kb/HT213488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32205.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEV6BR4MTI3CEWK2YU2HQZUW5FAS3FEY/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32205
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220915-0003/
- https://www.debian.org/security/2022/dsa-5197
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
