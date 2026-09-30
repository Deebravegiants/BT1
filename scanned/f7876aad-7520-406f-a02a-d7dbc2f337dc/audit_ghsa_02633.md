# [H] Basic auth bypass in esphome

## Summary
Severity: High
Advisory: GHSA-48mj-p7x2-5jfm
CVE: CVE-2021-41104
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-48mj-p7x2-5jfm
Type: github-advisory

## Affected
- PyPI: `esphome` — affected >=0 <2021.9.2

## Details
### Impact

Anyone with web_server enabled and HTTP basic auth configured on 2021.9.1 or older

`web_server` allows OTA update without checking user defined basic auth username & password

### Patches

Patch released in 2021.9.2

### Workarounds

Disable/remove `web_server`

## References
- https://github.com/esphome/esphome/security/advisories/GHSA-48mj-p7x2-5jfm
- https://nvd.nist.gov/vuln/detail/CVE-2021-41104
- https://github.com/esphome/esphome/pull/2409
- https://github.com/esphome/esphome/commit/2234f6aacf8cc653307fed80f3750317a82c4f83
- https://github.com/esphome/esphome/commit/be965a60eba6bb769e2a5afdbc8eed132f077a59
- https://github.com/esphome/esphome
- https://github.com/esphome/esphome/releases/tag/2021.9.2
- https://github.com/pypa/advisory-database/tree/main/vulns/esphome/PYSEC-2021-351.yaml
