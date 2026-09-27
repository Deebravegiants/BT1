# [C] CVE-2026-30079

## Summary
Severity: Critical
Advisory: CVE-2026-30079
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-30079
Type: osv

## Details
In OpenAirInterface V2.2.0 AMF, Out of sequence messages causes incorrect state transition during UE registration procedure. This allows authentication to be bypassed completely. If a SecurityModeComplete message is sent after InitialUERegistration, a registration reject is received followed by a registration accept! This leads the UE to be registered without proper authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30079.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30079
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/issues/77
