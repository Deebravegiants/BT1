# [H] Apollo Router's Compressed Payloads do not respect HTTP Payload Limits

## Summary
Severity: High
Advisory: GHSA-cgqf-3cq5-wvcj
CVE: CVE-2024-28101
CWE: CWE-409
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-cgqf-3cq5-wvcj
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=0.9.5 <1.40.2

## Details
### Impact
The Apollo Router is a configurable, high-performance graph router written in Rust to run a federated supergraph that uses Apollo Federation. Affected versions are subject to a Denial-of-Service (DoS) type vulnerability. When receiving compressed HTTP payloads, affected versions of the Router evaluate the `limits.http_max_request_bytes` configuration option after the entirety of the compressed payload is decompressed. If affected versions of the Router receive highly compressed payloads, this could result in significant memory consumption while the compressed payload is expanded. 

### Patches
Router version 1.40.2 has a fix for the vulnerability.

### Workarounds
If you are unable to upgrade, you may be able to implement mitigations at proxies or load balancers positioned in front of your Router fleet (e.g. Nginx, HAProxy, or cloud-native WAF services) by creating limits on HTTP body upload size.

## References
- https://github.com/apollographql/router/security/advisories/GHSA-cgqf-3cq5-wvcj
- https://github.com/apollographql/router/commit/9e9527c73c8f34fc8438b09066163cd42520f413
- https://github.com/apollographql/router
