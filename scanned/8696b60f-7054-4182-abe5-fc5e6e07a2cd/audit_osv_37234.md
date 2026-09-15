# [H] CVE-2026-30077

## Summary
Severity: High
Advisory: CVE-2026-30077
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-30077
Type: osv

## Details
OpenAirInterface V2.2.0 AMF crashes when it fails to decode the message. Not all decode failures result in a crash. But the crash is consistent for particular inputs. An example input in hex stream is 80 00 00 0E 00 00 01 00 0F 80 02 02 40 00 58 00 01 88.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30077.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30077
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/issues/76
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/merge_requests/414
