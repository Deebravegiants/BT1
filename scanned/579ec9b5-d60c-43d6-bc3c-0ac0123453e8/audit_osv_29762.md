# [M] CVE-2024-46613

## Summary
Severity: Medium
Advisory: CVE-2024-46613
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2024-46613
Type: osv

## Details
WeeChat before 4.4.2 has an integer overflow and resultant buffer overflow at core/core-string.c when there are more than two billion items in a list. This affects string_free_split_shared , string_free_split, string_free_split_command, and string_free_split_tags.

## References
- https://weechat.org/doc/weechat/security/WSA-2024-1/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46613.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46613
- https://github.com/weechat/weechat/issues/2178
