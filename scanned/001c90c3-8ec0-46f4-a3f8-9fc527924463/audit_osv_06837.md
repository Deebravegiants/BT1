# [H] BIT-modsecurity-2022-48279

## Summary
Severity: High
Advisory: BIT-modsecurity-2022-48279
Aliases: BIT-modsecurity2-2022-48279, CVE-2022-48279
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-modsecurity-2022-48279
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=0 <2.9.6

## Details
In ModSecurity before 2.9.6 and 3.x before 3.0.8, HTTP multipart requests were incorrectly parsed and could bypass the Web Application Firewall. NOTE: this is related to CVE-2022-39956 but can be considered independent changes to the ModSecurity (C language) codebase.

## References
- https://coreruleset.org/20220919/crs-version-3-3-3-and-3-2-2-covering-several-cves/
- https://github.com/SpiderLabs/ModSecurity/pull/2795
- https://github.com/SpiderLabs/ModSecurity/pull/2797
- https://github.com/SpiderLabs/ModSecurity/releases/tag/v2.9.6
- https://github.com/SpiderLabs/ModSecurity/releases/tag/v3.0.8
- https://lists.debian.org/debian-lts-announce/2023/01/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/52TGCZCOHYBDCVWJYNN2PS4QLOHCXWTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SYRTXTOQQI6SB2TLI5QXU76DURSLS4XI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WCH6JM4I4MD4YABYFHSBDDOUFDGIFJKL/
- https://nvd.nist.gov/vuln/detail/CVE-2022-48279
