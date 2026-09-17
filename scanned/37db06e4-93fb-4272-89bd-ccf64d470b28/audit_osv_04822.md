# [H] Envoy: Abnormal process termination in DNS UDP filter

## Summary
Severity: High
Advisory: BIT-envoy-2026-48497
Aliases: CVE-2026-48497, GHSA-j6g2-wf95-q66q
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-48497
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.1

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to 1.35.11, 1.36.7, 1.37.3, and 1.38.1, in cases where UDP DNS filter is configured with local resolution containing a name with the length of 255 octets or remote resolution for a name of 255 octets long can complete successfully, a query with such name will result in abnormal process termination. The abnormal process termination is triggered by an invalid runtime precondition that the query name is strictly less than 255 octets, contradicting DNS specification rfc1035#section-2.3.4 that the name can be 255 or less octets. This vulnerability is fixed in 1.35.11, 1.36.7, 1.37.3, and 1.38.1.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-j6g2-wf95-q66q
- https://nvd.nist.gov/vuln/detail/CVE-2026-48497
