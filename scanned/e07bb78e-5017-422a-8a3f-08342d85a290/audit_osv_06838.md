# [H] BIT-modsecurity-2023-24021

## Summary
Severity: High
Advisory: BIT-modsecurity-2023-24021
Aliases: BIT-modsecurity2-2023-24021, CVE-2023-24021
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-modsecurity-2023-24021
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=0 <2.9.7

## Details
Incorrect handling of '\0' bytes in file uploads in ModSecurity before 2.9.7 may allow for Web Application Firewall bypasses and buffer over-reads on the Web Application Firewall when executing rules that read the FILES_TMP_CONTENT collection.

## References
- https://github.com/SpiderLabs/ModSecurity/pull/2857
- https://github.com/SpiderLabs/ModSecurity/pull/2857/commits/4324f0ac59f8225aa44bc5034df60dbeccd1d334
- https://github.com/SpiderLabs/ModSecurity/releases/tag/v2.9.7
- https://lists.debian.org/debian-lts-announce/2023/01/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/52TGCZCOHYBDCVWJYNN2PS4QLOHCXWTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SYRTXTOQQI6SB2TLI5QXU76DURSLS4XI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WCH6JM4I4MD4YABYFHSBDDOUFDGIFJKL/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24021
