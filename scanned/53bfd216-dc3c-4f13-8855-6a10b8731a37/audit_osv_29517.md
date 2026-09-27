# [C] Remote Code Execution Vulnerability in MEGABOT

## Summary
Severity: Critical
Advisory: CVE-2024-43404
Aliases: GHSA-vhxp-4hwq-w3p2
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-43404
Type: osv

## Details
MEGABOT is a fully customized Discord bot for learning and fun. The `/math` command and functionality of MEGABOT versions < 1.5.0 contains a remote code execution vulnerability due to a Python `eval()`. The vulnerability allows an attacker to inject Python code into the `expression` parameter when using `/math` in any Discord channel. This vulnerability impacts any discord guild utilizing MEGABOT. This vulnerability was fixed in  release version 1.5.0.

## References
- https://github.com/NicPWNs/MEGABOT/releases/tag/v1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43404.json
- https://github.com/NicPWNs/MEGABOT/security/advisories/GHSA-vhxp-4hwq-w3p2
- https://nvd.nist.gov/vuln/detail/CVE-2024-43404
- https://github.com/NicPWNs/MEGABOT/issues/137
- https://github.com/NicPWNs/MEGABOT/commit/71e79e5581ea36313700385b112d863053fb7ed6
- https://github.com/NicPWNs/MEGABOT/pull/138
