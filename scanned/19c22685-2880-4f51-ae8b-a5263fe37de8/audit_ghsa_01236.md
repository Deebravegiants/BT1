# [H] Denial of Service in mqtt

## Summary
Severity: High
Advisory: GHSA-hg78-c92r-hvwr
CVE: CVE-2016-1000242
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-hg78-c92r-hvwr
Type: github-advisory

## Affected
- npm: `mqtt` — affected >=0 <1.0.0

## Details
Affected versions of `mqtt` will cause the node process to crash when receiving specially crafted MQTT packets, making the application vulnerable to a denial of service condition.



## Recommendation

Update to v1.0.0 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000242
- https://github.com/mqttjs/MQTT.js
- https://github.com/mqttjs/MQTT.js/blob/388a084d7803934b18b43c1146c817deaa1396b1/lib/parse.js#L230
- https://snyk.io/vuln/npm:mqtt:20160817
- https://www.npmjs.com/advisories/140
