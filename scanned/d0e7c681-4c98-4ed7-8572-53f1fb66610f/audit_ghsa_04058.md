# [H] Improper Input Validation and Buffer Over-read in mqtt-packet

## Summary
Severity: High
Advisory: GHSA-wv67-9jq7-8r69
CVE: CVE-2019-5432
CWE: CWE-125, CWE-126
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-wv67-9jq7-8r69
Type: github-advisory

## Affected
- npm: `mqtt-packet` — affected >=0 <3.5.1
- npm: `mqtt-packet` — affected >=4.0.0 <4.1.3
- npm: `mqtt-packet` — affected >=5.0.0 <5.6.1
- npm: `mqtt-packet` — affected >=6.0.0 <6.1.2

## Details
A specifically malformed MQTT Subscribe packet crashes MQTT Brokers using the mqtt-packet module versions < 3.5.1, 4.0.0 - 4.1.3, 5.0.0 - 5.6.1, 6.0.0 - 6.1.2 for decoding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5432
- https://hackerone.com/reports/541354
