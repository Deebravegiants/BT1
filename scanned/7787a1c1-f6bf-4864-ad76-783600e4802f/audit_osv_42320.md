# [M] httpd mod_auth directory protection bypassed by a doubled slash in the request path

## Summary
Severity: Medium
Advisory: CVE-2026-66835
Aliases: EEF-CVE-2026-66835, GHSA-r4vv-vc2c-2fw6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-66835
Type: osv

## Details
Path Equivalence vulnerability in Erlang/OTP inets httpd allows a remote unauthenticated attacker to read files inside a mod_auth protected directory by prefixing the request path with an extra slash.

httpd_request:validate_uri/1 normalises the request URI with uri_string:normalize/1, which performs RFC 3986 dot-segment removal but does not collapse empty path segments, so a doubled slash survives. mod_alias:real_name/3 concatenates the document root with that URI, and mod_auth:secret_path/3 then decides whether the result lies inside a protected directory block by running the configured directory path as an unanchored regular expression against it. The doubled slash breaks the contiguous substring the regex needs, so the request is treated as unprotected and no authentication challenge is issued, while mod_get opens the same path and the operating system collapses the doubled slash and returns the protected file. The same path mismatch also evades the per-path accounting in mod_security.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-66835.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-66835
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66835.json
- https://github.com/erlang/otp/security/advisories/GHSA-r4vv-vc2c-2fw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-66835
- https://github.com/erlang/otp/commit/9641944a2efbf55bea760f8ff7ba777fe3a0961c
- https://github.com/erlang/otp/commit/bac19eb3dbd96cc49b6d8cabc1c04248bf8c79f6
- https://github.com/erlang/otp/commit/d8878dec0ececc2eab18e47bb18b472f224ca633
- https://github.com/erlang/otp
