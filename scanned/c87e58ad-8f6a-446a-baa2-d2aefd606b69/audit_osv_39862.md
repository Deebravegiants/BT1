# [C] epa4all Security Incident: Implement keystore based on Telematik TSL, implement hostname check and certificate check for lib-vau

## Summary
Severity: Critical
Advisory: CVE-2026-48021
Aliases: GHSA-vvh7-x6c7-46gh
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-48021
Type: osv

## Details
In epa4all, prior to version 2026-05-20, an attacker who can intercept the TLS connection between epa4all and the ePA backend can complete the VAU handshake with attacker-controlled keys and obtain the session encryption keys. All inner HTTP traffic (patient consent decisions, medication data, document operations, authorization tokens, and entitlement queries) becomes readable and modifiable. The attacker can also inject arbitrary requests through the hijacked channel. This issue has been patched in version 2026-05-20.

## References
- https://github.com/med-united/epa4all/releases/tag/2026-05-20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48021.json
- https://github.com/med-united/epa4all/security/advisories/GHSA-vvh7-x6c7-46gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48021
- https://www.machinespirits.com/advisory/aa49f0
