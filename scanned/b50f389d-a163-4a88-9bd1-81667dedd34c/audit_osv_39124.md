# [H] Vanetza: Remote Denial of Service via Uncaught Exception in ASN.1/OER Parsing

## Summary
Severity: High
Advisory: CVE-2026-43988
Aliases: GHSA-j6cj-rp87-mfrx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-43988
Type: osv

## Details
Vanetza is an open-source implementation of the ETSI C-ITS protocol suite. In 26.02 and earlier, a denial-of-service vulnerability was identified in the ASN.1/OER parsing pipeline of Vanetza. When processing malformed network packets containing corrupted ASN.1/OER structures (e.g., invalid length fields or malformed certificate encoding), the ASN.1 wrapper (asn1c_wrapper.cpp) raises a std::runtime_error. This exception is not caught at the parsing boundary and propagates to std::terminate, resulting in process termination. This vulnerability is fixed with commit 62dfe58a8342512b6e1947d75821402ada524f1a.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43988.json
- https://github.com/riebl/vanetza/security/advisories/GHSA-j6cj-rp87-mfrx
- https://nvd.nist.gov/vuln/detail/CVE-2026-43988
- https://github.com/riebl/vanetza/commit/62dfe58a8342512b6e1947d75821402ada524f1a
