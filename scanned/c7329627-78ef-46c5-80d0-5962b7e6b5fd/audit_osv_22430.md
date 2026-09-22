# [M] Buffer Overflow on creating key transport blob in GOST Engine

## Summary
Severity: Medium
Advisory: CVE-2022-29242
Aliases: GHSA-2rmw-8wpg-vgw5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-24
Source: https://osv.dev/vulnerability/CVE-2022-29242
Type: osv

## Details
GOST engine is a reference implementation of the Russian GOST crypto algorithms for OpenSSL. TLS clients using GOST engine when ciphersuite `TLS_GOSTR341112_256_WITH_KUZNYECHIK_CTR_OMAC` is agreed and the server uses 512 bit GOST secret keys are vulnerable to buffer overflow. GOST engine version 3.0.1 contains a patch for this issue. Disabling ciphersuite `TLS_GOSTR341112_256_WITH_KUZNYECHIK_CTR_OMAC` is a possible workaround.

## References
- https://github.com/gost-engine/engine/releases/tag/v3.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29242.json
- https://github.com/gost-engine/engine/security/advisories/GHSA-2rmw-8wpg-vgw5
- https://nvd.nist.gov/vuln/detail/CVE-2022-29242
- https://github.com/gost-engine/engine/commit/7df766124f87768b43b9e8947c5a01e17545772c
- https://github.com/gost-engine/engine/commit/b2b4d629f100eaee9f5942a106b1ccefe85b8808
- https://github.com/gost-engine/engine/commit/c6655a0b620a3e31f085cc906f8073fe81b2fad3
