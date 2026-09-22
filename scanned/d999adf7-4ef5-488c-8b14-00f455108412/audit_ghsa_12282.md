# [H] OpenSSL gem for Ruby using inadequate encryption strength

## Summary
Severity: High
Advisory: GHSA-6h88-qjpv-p32m
CVE: CVE-2016-7798
CWE: CWE-326
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-6h88-qjpv-p32m
Type: github-advisory

## Affected
- RubyGems: `openssl` — affected >=0 <2.0.0

## Details
The OpenSSL gem for Ruby uses the same initialization vector (IV) in GCM Mode (aes-*-gcm) when the IV is set before the key, which makes it easier for context-dependent attackers to bypass the encryption protection mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7798
- https://github.com/ruby/openssl/issues/49
- https://github.com/ruby/openssl/commit/8108e0a6db133f3375608303fdd2083eb5115062
- https://github.com/advisories/GHSA-6h88-qjpv-p32m
- https://github.com/ruby/openssl
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openssl/CVE-2016-7798.yml
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://web.archive.org/web/20210121065227/https://www.securityfocus.com/bid/93031/info
- https://www.debian.org/security/2017/dsa-3966
- http://www.openwall.com/lists/oss-security/2016/09/19/9
- http://www.openwall.com/lists/oss-security/2016/09/30/6
- http://www.openwall.com/lists/oss-security/2016/10/01/2
