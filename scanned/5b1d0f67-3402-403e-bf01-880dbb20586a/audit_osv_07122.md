# [H] BIT-node-2021-44531

## Summary
Severity: High
Advisory: BIT-node-2021-44531
Aliases: BIT-node-min-2021-44531, CVE-2021-44531
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-44531
Type: osv

## Affected
- Bitnami: `node` — affected >=17.0.0 <17.3.1

## Details
Accepting arbitrary Subject Alternative Name (SAN) types, unless a PKI is specifically defined to use a particular SAN type, can result in bypassing name-constrained intermediates. Node.js < 12.22.9, < 14.18.3, < 16.13.2, and < 17.3.1 was accepting URI SAN types, which PKIs are often not defined to use. Additionally, when a protocol allows URI SANs, Node.js did not match the URI correctly.Versions of Node.js with the fix for this disable the URI SAN type when checking a certificate against a hostname. This behavior can be reverted through the --security-revert command-line option.

## References
- https://hackerone.com/reports/1429694
- https://nodejs.org/en/blog/vulnerability/jan-2022-security-releases/
- https://security.netapp.com/advisory/ntap-20220325-0007/
- https://www.debian.org/security/2022/dsa-5170
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-44531
