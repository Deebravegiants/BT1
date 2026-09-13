# [M] CVE-2016-7420

## Summary
Severity: Medium
Advisory: CVE-2016-7420
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-16
Source: https://osv.dev/vulnerability/CVE-2016-7420
Type: osv

## Details
Crypto++ (aka cryptopp) through 5.6.4 does not document the requirement for a compile-time NDEBUG definition disabling the many assert calls that are unintended in production use, which might allow context-dependent attackers to obtain sensitive information by leveraging access to process memory after an assertion failure, as demonstrated by reading a core dump.

## References
- http://www.openwall.com/lists/oss-security/2023/09/28/2
- http://www.openwall.com/lists/oss-security/2023/09/28/4
- http://www.openwall.com/lists/oss-security/2025/11/14/5
- http://www.securityfocus.com/bid/92988
- http://www.openwall.com/lists/oss-security/2016/09/15/12
- http://www.openwall.com/lists/oss-security/2016/09/16/1
- https://github.com/weidai11/cryptopp/commit/553049ba297d89d9e8fbf2204acb40a8a53f5cd6
- https://github.com/weidai11/cryptopp/issues/277
