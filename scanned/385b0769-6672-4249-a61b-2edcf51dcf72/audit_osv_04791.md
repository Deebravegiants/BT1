# [H] Envoy crashes in QuicheDataReader::PeekVarInt62Length()

## Summary
Severity: High
Advisory: BIT-envoy-2024-32975
Aliases: CVE-2024-32975, GHSA-g9mq-6v96-cpqc
Ecosystem: Bitnami
Published: 2024-06-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-32975
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.2

## Details
Envoy is a cloud-native, open source edge and service proxy. There is a crash at `QuicheDataReader::PeekVarInt62Length()`. It is caused by integer underflow in the `QuicStreamSequencerBuffer::PeekRegion()` implementation.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-g9mq-6v96-cpqc
- https://nvd.nist.gov/vuln/detail/CVE-2024-32975
