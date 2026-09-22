# [H] Uncontrolled Resource Consumption in promhttp

## Summary
Severity: High
Advisory: GHSA-cg3q-j54f-5p7p
CVE: CVE-2022-21698
CWE: CWE-400, CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-cg3q-j54f-5p7p
Type: github-advisory

## Affected
- Go: `github.com/prometheus/client_golang` — affected >=0 <1.11.1

## Details
This is the Go client library for Prometheus. It has two separate parts, one for instrumenting application code, and one for creating clients that talk to the Prometheus HTTP API. client_golang is the instrumentation library for Go applications in Prometheus, and the promhttp package in client_golang provides tooling around HTTP servers and clients.

### Impact

HTTP server susceptible to a Denial of Service through unbounded cardinality, and potential memory exhaustion, when handling requests with non-standard HTTP methods.

###  Affected Configuration

In order to be affected, an instrumented software must

* Use any of `promhttp.InstrumentHandler*` middleware except `RequestsInFlight`.
* Do not filter any specific methods (e.g GET) before middleware.
* Pass metric with `method` label name to our middleware.
* Not have any firewall/LB/proxy that filters away requests with unknown `method`.

### Patches

* https://github.com/prometheus/client_golang/pull/962
* https://github.com/prometheus/client_golang/pull/987

### Workarounds

If you cannot upgrade to [v1.11.1 or above](https://github.com/prometheus/client_golang/releases/tag/v1.11.1), in order to stop being affected you can:

* Remove `method` label name from counter/gauge you use in the InstrumentHandler.
* Turn off affected promhttp handlers.
* Add custom middleware before promhttp handler that will sanitize the request method given by Go http.Request.
* Use a reverse proxy or web application firewall, configured to only allow a limited set of methods.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in https://github.com/prometheus/client_golang
* Email us at `prometheus-team@googlegroups.com`

## References
- https://github.com/prometheus/client_golang/security/advisories/GHSA-cg3q-j54f-5p7p
- https://nvd.nist.gov/vuln/detail/CVE-2022-21698
- https://github.com/prometheus/client_golang/pull/962
- https://github.com/prometheus/client_golang/pull/987
- https://pkg.go.dev/vuln/GO-2022-0322
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZY2SLWOQR4ZURQ7UBRZ7JIX6H6F5JHJR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZKORFJTRRDJCWBTJPISKKCVMMMJBIRLG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SASRKYHT5ZFSVMJUQUG3UAEQRJYGJKAR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RN7JGC2LVHPEGSJYODFUV5FEKPBVG4D7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MH6ALXEQXIFQRQFNJ5Y2MJ5DFPIX76VN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KBMVIQFKQDSSTHVVJWJ4QH6TW3JVB7XZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J5WPM42UR6XIBQNQPNQHM32X7S4LJTRX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HLAQRRGNSO5MYCPAXGPH2OCSHOGHSQMQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FY3N7H6VSDZM37B4SKM2PFFCUWU7QYWN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DLUJZV3HBP56ADXU6QH2V7RNYUPMVBXQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AK7CJBCGERCRXYUR2EWDSSDVAQMTAZGX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7V7I72LSQ3IET3QJR6QPAVGJZ4CBDLN5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5OGNAFVXSMTTT2UPH6CS3IH6L3KM42Q7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4KDETHL5XCT6RZN2BBNOCEXRZ2W3SFU3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3L6GDN5S5QZSCFKWD3GKL2RDZQ6B4UWA
