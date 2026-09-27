# [H] MQTT does not validate hostnames

## Summary
Severity: High
Advisory: GHSA-9c5q-w6gr-fxcq
CVE: CVE-2025-12790
CWE: CWE-29
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-9c5q-w6gr-fxcq
Type: github-advisory

## Affected
- RubyGems: `mqtt` — affected >=0 <0.7.0

## Details
A flaw was found in Rubygem MQTT. By default, the package used to not have hostname validation, resulting in possible Man-in-the-Middle (MITM) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12790
- https://access.redhat.com/security/cve/CVE-2025-12790
- https://bugzilla.redhat.com/show_bug.cgi?id=2413004
- https://github.com/njh/ruby-mqtt/blob/main/NEWS.md#ruby-mqtt-version-070-2025-10-29
- http://github.com/njh/ruby-mqtt
