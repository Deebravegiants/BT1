# [M] Apache APISIX: Identity spoofing issue in APISIX opa plugin

## Summary
Severity: Medium
Advisory: BIT-apisix-2026-49231
Aliases: CVE-2026-49231
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-49231
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.5.0 <3.18.0

## Details
Authentication Bypass by Spoofing vulnerability in opa plugin.

An attacker could relay spoofed identity headers to upstream capitalising on non-default configuration in opa plugin.

This could allow the attacker to assume higher privileges on the upstream service.
This issue affects Apache APISIX: from 3.5.0 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/13
- https://lists.apache.org/thread/s1jd1vxm59p6ghx47xhmpjdk1cobo4hn
- https://nvd.nist.gov/vuln/detail/CVE-2026-49231
