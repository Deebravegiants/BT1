# [H] WeeChat has Non-Constant-Time Password Hash Comparison in Relay Authentication

## Summary
Severity: High
Advisory: CVE-2026-53525
Aliases: GHSA-vhv8-g2r9-cwcc
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53525
Type: osv

## Details
WeeChat (Wee Enhanced Environment for Chat) is a free chat client. In versions 0.3.1 through 4.9.0, the WeeChat relay authentication uses non-constant-time string comparison functions (weechat_strcasecmp and strcmp) to verify password hashes and plaintext passwords. An attacker can exploit timing differences to extract the server-computed hash character by character, then authenticate using the correct hash without knowing the password. Version 4.9.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53525.json
- https://github.com/weechat/weechat/security/advisories/GHSA-vhv8-g2r9-cwcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-53525
