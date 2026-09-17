# [M] ASN.1 TypeScript Library: Decoding an INTEGER could leak the underlying ArrayBuffer

## Summary
Severity: Medium
Advisory: CVE-2026-27452
Aliases: GHSA-h5rw-vxjr-8q79
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27452
Type: osv

## Details
ASN.1 TypeScript ESM library, including codecs for Basic Encoding Rules (BER) and Distinguished Encoding Rules (DER). In versions 11.0.5 and below, in some cases, decoding an INTEGER could leak the underlying ArrayBuffer. This issue is expected to be fixed in version 11.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27452.json
- https://github.com/JonathanWilbur/asn1-ts/security/advisories/GHSA-h5rw-vxjr-8q79
- https://nvd.nist.gov/vuln/detail/CVE-2026-27452
