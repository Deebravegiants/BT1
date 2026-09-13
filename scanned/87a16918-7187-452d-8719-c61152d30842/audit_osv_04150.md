# [M] Apache APISIX: wolf-rbac plugin Identity Spoofing

## Summary
Severity: Medium
Advisory: BIT-apisix-2026-44046
Aliases: CVE-2026-44046
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-44046
Type: osv

## Affected
- Bitnami: `apisix` — affected >=1.2.0 <3.17.0

## Details
Use of Less Trusted Source vulnerability in Apache APISIX.

Attacker can take advantage of wolf-rbac plugin under default configuration to potentially pollute logs with spoofed identity information and exploit IP based access control rules.
This issue affects Apache APISIX: from 1.2.0 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/6
- https://lists.apache.org/thread/xkshmps51b24yw0qckl5h5ddyv0x6qf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44046
