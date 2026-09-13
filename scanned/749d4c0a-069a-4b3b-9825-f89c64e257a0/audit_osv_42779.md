# [M] ESPHome web_server Plaintext Password Disclosure via JSON "value" Field

## Summary
Severity: Medium
Advisory: CVE-2026-71260
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71260
Type: osv

## Details
ESPHome through 2026.7.0-dev discloses plaintext passwords via its web_server component. In WebServer::text_json_ (esphome/components/web_server/web_server.cpp), a text entity configured with mode: password (TEXT_MODE_PASSWORD) has its JSON "state" field correctly masked as "********", but the same serialization path unconditionally writes the raw password into the JSON "value" field via set_json_icon_state_value/set_json_value.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71260.json
- https://github.com/esphome/esphome
- https://github.com/esphome/esphome/blob/dev/esphome/components/web_server/web_server.cpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-71260
