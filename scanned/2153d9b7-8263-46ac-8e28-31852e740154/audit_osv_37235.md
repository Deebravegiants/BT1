# [H] CVE-2026-30078

## Summary
Severity: High
Advisory: CVE-2026-30078
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-30078
Type: osv

## Details
OpenAirInterface V2.2.0 AMF crashes when it receives an NGAP message with invalid procedure code or invalid PDU-type. For example when the message specification requires InitiatingMessage but sent with successfulOutcome.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30078.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30078
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/issues/74
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/merge_requests/414
