# [H] CVE-2018-6340

## Summary
Severity: High
Advisory: CVE-2018-6340
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6340
Type: osv

## Details
The Memcache::getextendedstats function can be used to trigger an out-of-bounds read. Exploiting this issue requires control over memcached server hostnames and/or ports. This affects all supported versions of HHVM (3.30 and 3.27.4 and below).

## References
- https://hhvm.com/blog/2018/12/18/hhvm-3.30.1.html
- https://github.com/facebook/hhvm/commit/4bff3bfbe90d10451e4638c2118d1ad1117bb3e3
