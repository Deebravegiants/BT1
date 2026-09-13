# [M] ScriptAlias CGI targets bypass directory auth in inets httpd (mod_auth vs mod_cgi path mismatch)

## Summary
Severity: Medium
Advisory: CVE-2026-28808
Aliases: EEF-CVE-2026-28808, GHSA-3vhp-h532-mc3f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-28808
Type: osv

## Details
Incorrect Authorization vulnerability in Erlang OTP (inets modules) allows unauthenticated access to CGI scripts protected by directory rules when served via script_alias.

When script_alias maps a URL prefix to a directory outside DocumentRoot, mod_auth evaluates directory-based access controls against the DocumentRoot-relative path while mod_cgi executes the script at the ScriptAlias-resolved path. This path mismatch allows unauthenticated access to CGI scripts that directory rules were meant to protect.

This vulnerability is associated with program files lib/inets/src/http_server/mod_alias.erl, lib/inets/src/http_server/mod_auth.erl, and lib/inets/src/http_server/mod_cgi.erl.

This issue affects OTP from OTP 17.0 before OTP 26.2.5.19, OTP 27.3.4.10, and OTP 28.4.2, corresponding to inets from 5.10 before 9.1.0.6, 9.3.2.4, and 9.6.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-28808.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-28808
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-28808.json
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://access.redhat.com/security/cve/CVE-2026-28808
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28808.json
- https://github.com/erlang/otp/security/advisories/GHSA-3vhp-h532-mc3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-28808
- https://bugzilla.redhat.com/show_bug.cgi?id=2455909
- https://github.com/erlang/otp/commit/07b8f441ca711f9812fad9e9115bab3c3aa92f79
- https://github.com/erlang/otp/commit/8fc71ac6af4fbcc54103bec2983ef22e82942688
- https://github.com/erlang/otp/commit/9dfa0c51eac97866078e808dec2183cb7871ff7c
- https://github.com/erlang/otp
