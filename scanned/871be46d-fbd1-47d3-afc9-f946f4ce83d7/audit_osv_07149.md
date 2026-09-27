# [M] BIT-node-2024-21890

## Summary
Severity: Medium
Advisory: BIT-node-2024-21890
Aliases: BIT-node-min-2024-21890, CVE-2024-21890
Ecosystem: Bitnami
Published: 2024-06-04
Source: https://osv.dev/vulnerability/BIT-node-2024-21890
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.2

## Details
The Node.js Permission Model does not clarify in the documentation that wildcards should be only used as the last character of a file path. For example:
```
 --allow-fs-read=/home/node/.ssh/*.pub
```

will ignore `pub` and give access to everything after `.ssh/`.

This misleading documentation affects all users using the experimental permission model in Node.js 20 and Node.js 21.

Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://hackerone.com/reports/2257156
- https://security.netapp.com/advisory/ntap-20240315-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2024-21890
- https://github.com/nodejs/node/releases/tag/v20.11.1
- https://github.com/nodejs/node/releases/tag/v21.6.2
