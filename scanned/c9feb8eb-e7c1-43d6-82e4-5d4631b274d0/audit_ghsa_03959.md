# [H] Denial of Service in mqtt-packet

## Summary
Severity: High
Advisory: GHSA-g3r2-65gc-qpqc
CVE: CVE-2016-10523
CWE: CWE-400
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-g3r2-65gc-qpqc
Type: github-advisory

## Affected
- npm: `mqtt-packet` — affected >=0 <3.4.6
- npm: `mqtt-packet` — affected >=4.0.0 <4.0.5

## Details
Versions of `mqtt-packet` prior to 3.4.6, or 4.x prior to 4.0.5 are affected by a denial of service vulnerability wherein specific sequences of MQTT packets can crash the application.




## Recommendation

Version 3.x: Update to version 3.4.6 or later.
Version 4.x: Update to version 4.0.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10523
- https://github.com/mcollina/mosca/issues/393
- https://github.com/mqttjs/mqtt-packet/pull/8
- https://github.com/advisories/GHSA-g3r2-65gc-qpqc
- https://www.npmjs.com/advisories/75
