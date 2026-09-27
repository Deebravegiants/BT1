# [M] ALPINE-CVE-2026-3591

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-3591
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3591
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=9.20.0 <9.20.21-r0
- Alpine:v3.23: `bind` — affected >=9.20.0 <9.20.21-r0
- Alpine:v3.24: `bind` — affected >=9.20.0 <9.20.21-r0

## Details
A use-after-return vulnerability exists in the `named` server when handling DNS queries signed with SIG(0). Using a specially-crafted DNS request, an attacker may be able to cause an ACL to improperly (mis)match an IP address. In a default-allow ACL (denying only specific IP addresses), this may lead to unauthorized access. Default-deny ACLs should fail-secure.
This issue affects BIND 9 versions 9.20.0 through 9.20.20, 9.21.0 through 9.21.19, and 9.20.9-S1 through 9.20.20-S1.
BIND 9 versions 9.18.0 through 9.18.46 and 9.18.11-S1 through 9.18.46-S1 are NOT affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3591
