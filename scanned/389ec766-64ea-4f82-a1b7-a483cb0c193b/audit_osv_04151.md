# [C] Apache APISIX: Openid-connect plugin Identity Header Spoofing

## Summary
Severity: Critical
Advisory: BIT-apisix-2026-44087
Aliases: CVE-2026-44087
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-44087
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.3.0 <3.17.0

## Details
Insufficient Verification of Data Authenticity vulnerability in Apache APISIX.

The openid-connect plugin under default configuration has an attack surface that allows the attacker to spoof identity headers allowing the attacker to get unauthorized access the protected resources.
This issue affects Apache APISIX: from 2.3 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/7
- https://lists.apache.org/thread/72ryrgdssk6s2x9d6xn14bxyyl878xfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44087
