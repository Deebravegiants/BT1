# [H] Swift-corelibs-foundation denial of service in JSON decoding with JSONDecoder

## Summary
Severity: High
Advisory: GHSA-239c-6cv2-wwx8
CVE: CVE-2022-1642
CWE: CWE-704
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-07
Source: https://github.com/advisories/GHSA-239c-6cv2-wwx8
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-corelibs-foundation` — affected >=0 <5.6.2

## Details
### Impact

A program using swift-corelibs-foundation is vulnerable to a denial of service attack caused by a potentially malicious source producing a JSON document containing a type mismatch.

This vulnerability is caused by the interaction between a deserialization mechanism offered by the Swift standard library, the Codable protocol; and the JSONDecoder class offered by swift-corelibs-foundation, which can deserialize types that adopt the Codable protocol based on the content of a provided JSON document. When a type that adopts Codable requests the initialization of a field with an integer value, the JSONDecoder class uses a type-erased container with different accessor methods to attempt and coerce a corresponding JSON value and produce an integer. In the case the JSON value was a numeric literal with a floating-point portion, JSONDecoder used different type-eraser methods during validation than it did during the final casting of the value. The checked casting produces a deterministic crash due to this mismatch.

The JSONDecoder class is often wrapped by popular Swift-based web frameworks to parse the body of HTTP requests and perform basic type validation. This makes the attack low-effort: sending a specifically crafted JSON document during a request to these endpoints will cause them to crash.

The attack does not have any confidentiality or integrity risks in and of itself; the crash is produced deterministically by an abort function that ensures that execution does not continue in the face of this violation of assumptions. However, unexpected crashes can lead to violations of invariants in services, so it's possible that this attack can be used to trigger error conditions that escalate the risk. Producing a denial of service may also be the goal of an attacker in itself.

### Resolution

This issue is solved in Swift 5.6.2 for Linux and Windows. This issue was solved by ensuring that the same methods are invoked both when validating and during casting, so that no type mismatch occurs.

Swift for Linux and Windows versions are not ABI-interchangeable. To upgrade a service, its owner must update to this version of the Swift toolchain, then recompile and redeploy their software. The new version of Swift includes an updated swift-corelibs-foundation package.

The resolution is also included in recent development snapshots of Swift available on swift.org for those platforms.

Versions of Swift running on Darwin-based operating systems are not affected.

### Workarounds

Users that can control which payload is parsed with JSONDecoder can ensure that fields that are intended to initialize Swift integer types use a JSON numeric constant without a fractional part. This will avoid the crash, but it is rare that a user has full control on the JSON payload they will parse.

As a workaround, users that can alter their current software but cannot perform an upgrade can perform JSON parsing directly (e.g., through the JSONSerialization class) rather than using the JSONDecoder class.

## References
- https://github.com/apple/swift-corelibs-foundation/security/advisories/GHSA-239c-6cv2-wwx8
- https://nvd.nist.gov/vuln/detail/CVE-2022-1642
- https://github.com/apple/swift-corelibs-foundation/commit/b541491f73b39007a38f3ff5a0cbe89d09ef1614
- https://github.com/apple/swift-corelibs-foundation
