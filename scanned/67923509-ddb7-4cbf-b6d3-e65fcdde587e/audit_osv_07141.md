# [M] BIT-node-2023-32005

## Summary
Severity: Medium
Advisory: BIT-node-2023-32005
Aliases: BIT-node-min-2023-32005, CVE-2023-32005
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-32005
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.5.1

## Details
A vulnerability has been identified in Node.js version 20, affecting users of the experimental permission model when the --allow-fs-read flag is used with a non-* argument.

This flaw arises from an inadequate permission model that fails to restrict file stats through the `fs.statfs` API. As a result, malicious actors can retrieve stats from files that they do not have explicit read access to.

This vulnerability affects all users using the experimental permission model in Node.js 20.

Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2051224
- https://security.netapp.com/advisory/ntap-20231103-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2023-32005
