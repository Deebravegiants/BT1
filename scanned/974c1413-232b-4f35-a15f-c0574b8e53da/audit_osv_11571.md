# [C] CVE-2017-8807

## Summary
Severity: Critical
Advisory: CVE-2017-8807
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-11-16
Source: https://osv.dev/vulnerability/CVE-2017-8807
Type: osv

## Details
vbf_stp_error in bin/varnishd/cache/cache_fetch.c in Varnish HTTP Cache 4.1.x before 4.1.9 and 5.x before 5.2.1 allows remote attackers to obtain sensitive information from process memory because a VFP_GetStorage buffer is larger than intended in certain circumstances involving -sfile Stevedore transient objects.

## References
- http://www.securityfocus.com/bid/101886
- https://www.debian.org/security/2017/dsa-4034
- https://bugs.debian.org/881808
- https://github.com/varnishcache/varnish-cache/pull/2429
- http://varnish-cache.org/security/VSV00002.html
- https://github.com/varnishcache/varnish-cache/commit/176f8a075a963ffbfa56f1c460c15f6a1a6af5a7
