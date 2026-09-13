# [M] CVE-2019-25014

## Summary
Severity: Medium
Advisory: CVE-2019-25014
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-29
Source: https://osv.dev/vulnerability/CVE-2019-25014
Type: osv

## Details
A NULL pointer dereference was found in pkg/proxy/envoy/v2/debug.go getResourceVersion in Istio pilot before 1.5.0-alpha.0. If a particular HTTP GET request is made to the pilot API endpoint, it is possible to cause the Go runtime to panic (resulting in a denial of service to the istio-pilot application).

## References
- https://github.com/istio/istio/compare/1.4.2...1.5.0-alpha.0
- https://bugzilla.redhat.com/show_bug.cgi?id=1919066
