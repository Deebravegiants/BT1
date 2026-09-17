# [H] BIT-node-2023-30586

## Summary
Severity: High
Advisory: BIT-node-2023-30586
Aliases: BIT-node-min-2023-30586, CVE-2023-30586
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-30586
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.3.1

## Details
A privilege escalation vulnerability exists in Node.js 20 that allowed loading arbitrary OpenSSL engines when the experimental permission model is enabled, which can bypass and/or disable the permission model. The attack complexity is high. However, the crypto.setEngine() API can be used to bypass the permission model when called with a compatible OpenSSL engine. The OpenSSL engine can, for example, disable the permission model in the host process by manipulating the process's stack memory to locate the permission model Permission::enabled_ in the host process's heap memory. Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/1954535
- https://security.netapp.com/advisory/ntap-20230803-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2023-30586
