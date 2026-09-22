# [C] Apache APISIX: JWT Algorithm Confusion allows authentication bypass

## Summary
Severity: Critical
Advisory: BIT-apisix-2026-39999
Aliases: CVE-2026-39999
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-39999
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.2.0 <3.17.0

## Details
Authentication Bypass by Spoofing vulnerability in Apache APISIX.

The attacker can completely bypass authentication capitalising on certain configurations of jwt-auth plugin.
This issue affects Apache APISIX: from v2.2 through v3.16.0.

Users are recommended to upgrade to version v3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/5
- https://lists.apache.org/thread/nfopt8cnxd3k0rs1oxtr7lzxrdw4mojq
- https://nvd.nist.gov/vuln/detail/CVE-2026-39999
