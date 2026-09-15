# [M] Netty MQTT: Resource exhaustion in MqttDecoder

## Summary
Severity: Medium
Advisory: GHSA-jfg9-48mv-9qgx
CVE: CVE-2026-44248
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-jfg9-48mv-9qgx
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-mqtt` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-mqtt` — affected >=0 <4.1.133.Final

## Details
### Impact
The MQTT 5 header Properties section is parsed and buffered _before_ any message size limit is applied.

Specifically, in `MqttDecoder`, the `decodeVariableHeader()` method is called before the `bytesRemainingBeforeVariableHeader > maxBytesInMessage` check. The `decodeVariableHeader()` can call other methods which will call `decodeProperties()`. Effectively, Netty does not apply any limits to the size of the properties being decoded.

Additionally, because `MqttDecoder` extends `ReplayingDecoder`, Netty will repeatedly re-parse the enormous Properties sections and buffer the bytes in memory, until the entire thing parses to completion.

This can cause high resource usage in both CPU and memory.

### Resources
`ANT-2026-09608`
https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901027

## References
- https://github.com/netty/netty/security/advisories/GHSA-jfg9-48mv-9qgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44248
- https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901027
- https://github.com/netty/netty
