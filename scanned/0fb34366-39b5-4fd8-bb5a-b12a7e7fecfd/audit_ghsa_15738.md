# [H] DNSJava vulnerable to KeyTrap - Denial-of-Service Algorithmic Complexity Attacks

## Summary
Severity: High
Advisory: GHSA-crjg-w57m-rqqf
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-crjg-w57m-rqqf
Type: github-advisory

## Affected
- Maven: `dnsjava:dnsjava` — affected >=3.5.0 <3.6.0
- Maven: `org.jitsi:dnssecjava` — affected >=0

## Details
### Impact
Users using the `ValidatingResolver` for DNSSEC validation can run into CPU exhaustion with specially crafted DNSSEC-signed zones.

### Patches
Users should upgrade to dnsjava v3.6.0

### Workarounds
Although not recommended, only using a non-validating resolver, will remove the vulnerability. 

### References
https://www.athene-center.de/en/keytrap

## References
- https://github.com/dnsjava/dnsjava/security/advisories/GHSA-crjg-w57m-rqqf
- https://nvd.nist.gov/vuln/detail/CVE-2023-50387
- https://github.com/dnsjava/dnsjava/commit/07ac36a11578cc1bce0cd8ddf2fe568f062aee78
- https://github.com/dnsjava/dnsjava/commit/3ddc45ce8cdb5c2274e10b7401416f497694e1cf
- https://github.com/advisories/GHSA-8459-gg55-8qjj
- https://github.com/dnsjava/dnsjava
