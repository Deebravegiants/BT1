# [H] Zip bomb vulnerability in Envoy

## Summary
Severity: High
Advisory: BIT-envoy-2022-29225
Aliases: CVE-2022-29225, GHSA-75hv-2jjj-89hh
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-29225
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.22.1

## Details
Envoy is a cloud-native high-performance proxy. In versions prior to 1.22.1 secompressors accumulate decompressed data into an intermediate buffer before overwriting the body in the decode/encodeBody. This may allow an attacker to zip bomb the decompressor by sending a small highly compressed payload. Maliciously constructed zip files may exhaust system memory and cause a denial of service. Users are advised to upgrade. Users unable to upgrade may consider disabling decompression.

## References
- https://github.com/envoyproxy/envoy/commit/cb4ef0b09200c720dfdb07e097092dd105450343
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-75hv-2jjj-89hh
- https://nvd.nist.gov/vuln/detail/CVE-2022-29225
