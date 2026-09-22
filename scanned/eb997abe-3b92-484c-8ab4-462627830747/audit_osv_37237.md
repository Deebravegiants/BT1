# [H] CVE-2026-30080

## Summary
Severity: High
Advisory: CVE-2026-30080
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-30080
Type: osv

## Details
OpenAirInterface v2.2.0 accepts Security Mode Complete without any integrity protection. Configuration has supported integrity NIA1 and NIA2. But if an UE sends initial registration request with only security capability IA0, OpenAirInterface accepts and proceeds. This downgrade security context can lead to the possibility of replay attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30080.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30080
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/issues/78
