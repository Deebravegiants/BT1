# [H] CVE-2020-36420

## Summary
Severity: High
Advisory: CVE-2020-36420
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-15
Source: https://osv.dev/vulnerability/CVE-2020-36420
Type: osv

## Details
Polipo through 1.1.1, when NDEBUG is omitted, allows denial of service via a reachable assertion during parsing of a malformed Range header. NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- http://www.openwall.com/lists/oss-security/2021/07/18/1
- https://bugs.gentoo.org/755896
- https://github.com/jech/polipo/commit/4d42ca1b5849518762d110f34b6ce2e03d6df9ec
- https://www.openwall.com/lists/oss-security/2020/11/18/1
