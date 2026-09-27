# [H] BIT-node-2022-43548

## Summary
Severity: High
Advisory: BIT-node-2022-43548
Aliases: BIT-node-min-2022-43548, CVE-2022-43548
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2022-43548
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <19.0.1

## Details
A OS Command Injection vulnerability exists in Node.js versions <14.21.1, <16.18.1, <18.12.1, <19.0.1 due to an insufficient IsAllowedHost check that can easily be bypassed because IsIPAddress does not properly check if an IP address is invalid before making DBS requests allowing rebinding attacks.The fix for this issue in https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32212 was incomplete and this new CVE is to complete the fix.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00038.html
- https://nodejs.org/en/blog/vulnerability/november-2022-security-releases/
- https://security.netapp.com/advisory/ntap-20230120-0004/
- https://security.netapp.com/advisory/ntap-20230427-0007/
- https://www.debian.org/security/2023/dsa-5326
- https://nvd.nist.gov/vuln/detail/CVE-2022-43548
