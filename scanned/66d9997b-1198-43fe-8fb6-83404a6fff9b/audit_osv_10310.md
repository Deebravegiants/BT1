# [H] CVE-2017-14919

## Summary
Severity: High
Advisory: CVE-2017-14919
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/CVE-2017-14919
Type: osv

## Details
Node.js before 4.8.5, 6.x before 6.11.5, and 8.x before 8.8.0 allows remote attackers to cause a denial of service (uncaught exception and crash) by leveraging a change in the zlib module 1.2.9 making 8 an invalid value for the windowBits parameter.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-470355.html
- http://www.securityfocus.com/bid/101881
- https://nodejs.org/en/blog/release/v4.8.5/
- https://nodejs.org/en/blog/release/v6.11.5/
- https://nodejs.org/en/blog/release/v8.8.0/
- https://nodejs.org/en/blog/vulnerability/oct-2017-dos/
