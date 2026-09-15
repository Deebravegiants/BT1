# [M] CVE-2020-28168

## Summary
Severity: Medium
Advisory: CVE-2020-28168
Aliases: GHSA-4w2v-q235-vp99
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2020-28168
Type: osv

## Details
Axios NPM package 0.21.0 contains a Server-Side Request Forgery (SSRF) vulnerability where an attacker is able to bypass a proxy by providing a URL that responds with a redirect to a restricted host or IP address.

## References
- https://lists.apache.org/thread.html/r25d53acd06f29244b8a103781b0339c5e7efee9099a4d52f0c230e4a%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r954d80fd18e9dafef6e813963eb7e08c228151c2b6268ecd63b35d1f%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rdfd2901b8b697a3f6e2c9c6ecc688fd90d7f881937affb5144d61d6e%40%3Ccommits.druid.apache.org%3E
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
- https://github.com/axios/axios/issues/3369
