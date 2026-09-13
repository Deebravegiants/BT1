# [H] Continued processing of requests after locally generated response

## Summary
Severity: High
Advisory: BIT-envoy-2021-32781
Aliases: CVE-2021-32781, GHSA-5vhv-gp9v-42qv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-32781
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.19.0 <1.19.1

## Details
Envoy is an open source L7 proxy and communication bus designed for large modern service oriented architectures. In affected versions after Envoy sends a locally generated response it must stop further processing of request or response data. However when local response is generated due the internal buffer overflow while request or response is processed by the filter chain the operation may not be stopped completely and result in accessing a freed memory block. A specifically constructed request delivered by an untrusted downstream or upstream peer in the presence of extensions that modify and increase the size of request or response bodies resulting in a Denial of Service when using extensions that modify and increase the size of request or response bodies, such as decompressor filter. Envoy versions 1.19.1, 1.18.4, 1.17.4, 1.16.5 contain fixes to address incomplete termination of request processing after locally generated response. As a workaround disable Envoy's decompressor, json-transcoder or grpc-web extensions or proprietary extensions that modify and increase the size of request or response bodies, if feasible.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-5vhv-gp9v-42qv
- https://www.envoyproxy.io/docs/envoy/v1.19.0/version_history/version_history
- https://nvd.nist.gov/vuln/detail/CVE-2021-32781
