# [H] CVE-2021-43825

## Summary
Severity: High
Advisory: CVE-2021-43825
Aliases: BIT-envoy-2021-43825, GHSA-h69p-g6xg-mhhh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-22
Source: https://osv.dev/vulnerability/CVE-2021-43825
Type: osv

## Details
Envoy is an open source edge and service proxy, designed for cloud-native applications. Sending a locally generated response must stop further processing of request or response data. Envoy tracks the amount of buffered request and response data and aborts the request if the amount of buffered data is over the limit by sending 413 or 500 responses. However when the buffer overflows while response is processed by the filter chain the operation may not be aborted correctly and result in accessing a freed memory block. If this happens Envoy will crash resulting in a denial of service.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-h69p-g6xg-mhhh
- https://github.com/envoyproxy/envoy/commit/148de954ed3585d8b4298b424aa24916d0de6136
