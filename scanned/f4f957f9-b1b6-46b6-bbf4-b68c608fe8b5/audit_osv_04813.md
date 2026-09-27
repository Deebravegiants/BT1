# [H] Envoy: Segmentation fault when using %REQUESTED_SERVER_NAME% in log format

## Summary
Severity: High
Advisory: BIT-envoy-2026-47220
Aliases: CVE-2026-47220, GHSA-j9wh-4qfm-wf2v
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-47220
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.37.0 until 1.37.5 and 1.38.3, when the %REQUESTED_SERVER_NAME(X:Y)% is used in log format and host related options is specified, like HOST_FIRST, SNI_FIRST, it's possible to crash Envoy when the specified host header is missing in the request headers. This vulnerability is fixed in 1.37.5 and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-j9wh-4qfm-wf2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-47220
- https://access.redhat.com/security/cve/CVE-2026-47220
- https://bugzilla.redhat.com/show_bug.cgi?id=2493652
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-47220.json
