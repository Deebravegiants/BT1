# [M] CocoaMQTT: Denial of Service via Reachable Assertion in `PUBLISH` Packet Parsing 

## Summary
Severity: Medium
Advisory: GHSA-r3fr-7m74-q7g2
CVE: CVE-2026-30867
CWE: CWE-617
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-r3fr-7m74-q7g2
Type: github-advisory

## Affected
- SwiftURL: `CocoaMQTT` — affected >=0 <2.2.2

## Details
A vulnerability exists in the packet parsing logic of CocoaMQTT that allows an attacker (or a compromised/malicious MQTT broker) to remotely crash the host iOS/macOS/tvOS application.

The vulnerability is located in `Source/FramePublish.swift` during the extraction of the Topic string from the incoming byte array.

When parsing the Variable Header of a `PUBLISH` frame, the library reads the first two bytes to determine the `topicLength`. It then adds this length to the current position (`pos`) and attempts to slice the byte array to extract the string:

```swift
if let data = NSString(bytes: [UInt8](bytes[2...(pos-1)]), length: Int(len), encoding: String.Encoding.utf8.rawValue) {
    topic = data as String
}
```

If a packet is received where the Topic Length evaluates to `0` (e.g., `0x00 0x00`), the `len` variable becomes `0`, and `pos` evaluates to `2`.

The slicing logic dynamically calculates `bytes[2...(2-1)]`, which becomes **`bytes[2...1]`**. Swift's `ClosedRange` operator (`...`) requires the lower bound to be less than or equal to the upper bound. Because 2 is not less than 1, Swift detects an out-of-bounds access attempt and immediately triggers a runtime trap (`Fatal error: Range requires lowerBound <= upperBound`), crashing the host application.

If an attacker publishes this 4-byte malformed payload to a shared topic with the `RETAIN` flag set to true, the MQTT broker will persist the payload. Any time a vulnerable client connects and subscribes to that topic, the broker will automatically push the malformed packet. The app will instantly crash in the background before the user can even interact with it. This effectively "bricks" the mobile application (a persistent DoS) until the retained message is manually wiped from the broker database.

## References
- https://github.com/emqx/CocoaMQTT/security/advisories/GHSA-r3fr-7m74-q7g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-30867
- https://github.com/emqx/CocoaMQTT/pull/659
- https://github.com/emqx/CocoaMQTT/commit/010bca6f61b97d726252f61641d331a2bf82b338
- https://github.com/emqx/CocoaMQTT
- https://github.com/emqx/CocoaMQTT/releases/tag/2.2.2
