# [C] BIT-node-2023-39332

## Summary
Severity: Critical
Advisory: BIT-node-2023-39332
Aliases: BIT-node-min-2023-39332, CVE-2023-39332
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-39332
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.8.0

## Details
Various `node:fs` functions allow specifying paths as either strings or `Uint8Array` objects. In Node.js environments, the `Buffer` class extends the `Uint8Array` class. Node.js prevents path traversal through strings (see CVE-2023-30584) and `Buffer` objects (see CVE-2023-32004), but not through non-`Buffer` `Uint8Array` objects.

This is distinct from CVE-2023-32004 which only referred to `Buffer` objects. However, the vulnerability follows the same pattern using `Uint8Array` instead of `Buffer`.

Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2199818
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3N4NJ7FR4X4FPZUGNTQAPSTVB2HB2Y4A/
- https://security.netapp.com/advisory/ntap-20231116-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39332
- https://security.netapp.com/advisory/ntap-20241108-0002/
