# [M] EVerest allows null session ID to bypass session ID verification

## Summary
Severity: Medium
Advisory: CVE-2025-68140
Aliases: GHSA-w385-3jwp-x47x
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68140
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2025.9.0, once the validity of the received V2G message has been verified, it is checked whether the submitted session ID matches the registered one. However, if no session has been registered, the default value is 0. Therefore, a message submitted with a session ID of 0 is accepted, as it matches the registered value. This could allow unauthorized and anonymous indirect emission of MQTT messages and communication with V2G messages handlers, updating a session context. Version 2025.9.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68140.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-w385-3jwp-x47x
- https://nvd.nist.gov/vuln/detail/CVE-2025-68140
