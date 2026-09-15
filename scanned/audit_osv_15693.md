# [H] CVE-2019-18838

## Summary
Severity: High
Advisory: CVE-2019-18838
Aliases: GHSA-f2rv-4w6x-rwhc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-13
Source: https://osv.dev/vulnerability/CVE-2019-18838
Type: osv

## Details
An issue was discovered in Envoy 1.12.0. Upon receipt of a malformed HTTP request without a Host header, it sends an internally generated "Invalid request" response. This internally generated response is dispatched through the configured encoder filter chain before being sent to the client. An encoder filter that invokes route manager APIs that access a request's Host header causes a NULL pointer dereference, resulting in abnormal termination of the Envoy process.

## References
- https://groups.google.com/forum/#%21forum/envoy-users
- https://github.com/envoyproxy/envoy/commits/master
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-f2rv-4w6x-rwhc
