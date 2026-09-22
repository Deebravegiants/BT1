# [H] Serverpod client accepts any certificate

## Summary
Severity: High
Advisory: GHSA-h6x7-r5rg-x5fw
CVE: CVE-2024-29887
CWE: CWE-295
Ecosystem: Pub
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-h6x7-r5rg-x5fw
Type: github-advisory

## Affected
- Pub: `serverpod_client` — affected >=0 <1.2.6

## Details
This bug bypassed the validation of TSL certificates on all none web HTTP clients in the `serverpod_client` package. Making them susceptible to a man in the middle attack against encrypted traffic between the client device and the server. 

An attacker would need to be able to intercept the traffic and highjack the connection to the server for this vulnerability to be used. 

### Impact
All versions of `serverpod_client` pre `1.2.6`

### Patches
Upgrading to version `1.2.6` resolves this issue.

## References
- https://github.com/serverpod/serverpod/security/advisories/GHSA-h6x7-r5rg-x5fw
- https://nvd.nist.gov/vuln/detail/CVE-2024-29887
- https://github.com/serverpod/serverpod/commit/d55bf8d12967fc7955a875cb3e0f9693bd6d2c71
- https://github.com/serverpod/serverpod
