# [H] CVE-2018-12116

## Summary
Severity: High
Advisory: CVE-2018-12116
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-12116
Type: osv

## Details
Node.js: All versions prior to Node.js 6.15.0 and 8.14.0: HTTP request splitting: If Node.js can be convinced to use unsanitized user-provided Unicode data for the `path` option of an HTTP request, then data can be provided which will trigger a second, unexpected, and user-defined HTTP request to made to the same server.

## References
- https://access.redhat.com/errata/RHSA-2019:1821
- https://security.gentoo.org/glsa/202003-48
- https://nodejs.org/en/blog/vulnerability/november-2018-security-releases/
