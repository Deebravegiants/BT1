# [M] CVE-2018-12123

## Summary
Severity: Medium
Advisory: CVE-2018-12123
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-12123
Type: osv

## Details
Node.js: All versions prior to Node.js 6.15.0, 8.14.0, 10.14.0 and 11.3.0: Hostname spoofing in URL parser for javascript protocol: If a Node.js application is using url.parse() to determine the URL hostname, that hostname can be spoofed by using a mixed case "javascript:" (e.g. "javAscript:") protocol (other protocols are not affected). If security decisions are made about the URL based on the hostname, they may be incorrect.

## References
- https://access.redhat.com/errata/RHSA-2019:1821
- https://security.gentoo.org/glsa/202003-48
- https://security.netapp.com/advisory/ntap-20241213-0008/
- https://nodejs.org/en/blog/vulnerability/november-2018-security-releases/
