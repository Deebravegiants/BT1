# [M] Un-sanitized metric name or labels can be used to take over exported metrics

## Summary
Severity: Medium
Advisory: GHSA-x768-cvr2-345r
CVE: CVE-2024-28867
CWE: CWE-74
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-x768-cvr2-345r
Type: github-advisory

## Affected
- SwiftURL: `github.com/swift-server/swift-prometheus` — affected >=2.0.0-alpha.1 <2.0.0-alpha.2

## Details
### Impact

In code which applies _un-sanitized string values into metric names or labels_, like this:

```swift
let lang = try? request.query-get(String.self, at: "lang")
Counter (
  label: "language", 
  dimensions: [("lang", lang ?? "unknown" )]
)
```

an attacker could make use of this and send a `?lang` query parameter containing newlines, `}`  or similar characters which can lead to the attacker taking over the exported format -- including creating unbounded numbers of stored metrics, inflating server memory usage, or causing "bogus" metrics.

### Patches
The default strategy to sanitize labels was moved deeper into the library, preventing illegal characters from appearing in name, label keys and values.

Metric names and label names are now validated against the following requirement: `[a-zA-Z_:][a-zA-Z0-9_:]*` (for metric names) and `[a-zA-Z_][a-zA-Z0-9_]*` (for metric label names). Label values are not validated as they are allowed to contain any unicode characters. Developers _must_ validate labels themselves and not allow malicious input.

The approach taken here mirrors the approach taken in the Go reference implementation.

### Discussion

It is **strongly discouraged** to use un-sanitized user input as names or labels in general, because they can lead to un-bounded growth of metrics, even as this vulnerability is patched and result in a Denial-of-Service attack opportunity -- **regardless** how well the library is sanitizing the inputs. We strongly recommend only using a sanitized set of values for your metrics names and labels. E.g., a `"lang"` label, should only use an expected set of values that can be used, and ignore other ones -- otherwise a determined attacker could create one metric per different label key, leading to unbounded memory use growth as metrics with distinct values must be kept in memory.

**Validating label values:**

The library will **NOT** automatically validate and replace strings offered as label values.
Developers **must** validate label values themselves, and it is strongly recommended to only accept a well known set of values.

It is possible to configure the `PrometheusSanitizer` to apply whatever validation you deem necessary:

```swift
let mySanitizer = PrometheusSanitizer { metricName, labels in
  // ... your logic here ...
  (metricName, labels)
}

let registry = PrometheusCollectorRegistry(sanitizer: mySanitizer)
let factory = PrometheusMetricsFactory(factory: registry)

// swift-metrics
MetricsSystem.bootstrap(factory)
```



### Workarounds

Developers must validate user input before using it as metric names, label names or values. This follows common practice of not trusting any user input without sanitization.

### Credits

We would like to thank Jonas Dörr for bringing out attention to the issue.

## References
- https://github.com/swift-server/swift-prometheus/security/advisories/GHSA-x768-cvr2-345r
- https://nvd.nist.gov/vuln/detail/CVE-2024-28867
- https://github.com/swift-server/swift-prometheus/commit/bfcd4bbfabe11aae4b035424ee9724582e288501
- https://github.com/swift-server/swift-prometheus
