# [C] RADIUS Protocol under RFC2865 is vulnerable to forgery attacks.

## Summary
Severity: Critical
Advisory: CVE-2024-3596
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-3596
Type: osv

## Details
RADIUS Protocol under RFC 2865 is susceptible to forgery attacks by a local attacker who can modify any valid Response (Access-Accept, Access-Reject, or Access-Challenge) to any other response using a chosen-prefix collision attack against MD5 Response Authenticator signature.

## References
- http://www.openwall.com/lists/oss-security/2024/07/09/4
- https://cert-portal.siemens.com/productcert/html/ssa-364175.html
- https://cert-portal.siemens.com/productcert/html/ssa-770770.html
- https://datatracker.ietf.org/doc/draft-ietf-radext-deprecating-radius/
- https://datatracker.ietf.org/doc/html/rfc2865
- https://networkradius.com/assets/pdf/radius_and_md5_collisions.pdf
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2024-0014
- https://today.ucsd.edu/story/computer-scientists-discover-vulnerabilities-in-a-popular-security-protocol
- https://www.blastradius.fail/
- https://www.kb.cert.org/vuls/id/456537
- https://cert-portal.siemens.com/productcert/html/ssa-723487.html
- https://cert-portal.siemens.com/productcert/html/ssa-794185.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3596.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3596
- https://security.netapp.com/advisory/ntap-20240822-0001/
