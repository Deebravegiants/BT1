# [H] CoreWCF: Pre-authentication infinite-loop CPU exhaustion in CoreWCF net.tcp / net.pipe / net.uds framing handshake

## Summary
Severity: High
Advisory: GHSA-p86g-xrr2-pf7c
CVE: CVE-2026-54772
CWE: CWE-400, CWE-835
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-p86g-xrr2-pf7c
Type: github-advisory

## Affected
- NuGet: `CoreWCF.NetFramingBase` — affected >=0 <1.8.1
- NuGet: `CoreWCF.NetFramingBase` — affected >=1.9.0 <1.9.1

## Details
### Impact
An unauthenticated remote attacker can pin one server thread‑pool worker at 100 % CPU per connection. With a few connections, the CPU usage can be exhausted.

#### Preconditions
An attacker being able to reach a service which is exposing an endpoint using one of NetTcpBinding, NetNamedPipeBinding, or UnixDomainSocketBinding.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
None

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-p86g-xrr2-pf7c
- https://github.com/CoreWCF/CoreWCF
