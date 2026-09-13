# [H] adm-zip: Crafted ZIP file triggers 4GB memory allocation

## Summary
Severity: High
Advisory: GHSA-xcpc-8h2w-3j85
CVE: CVE-2026-39244
CWE: CWE-400, CWE-789
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-xcpc-8h2w-3j85
Type: github-advisory

## Affected
- npm: `adm-zip` — affected >=0 <0.6.0

## Details
adm-zip before 0.5.18 is vulnerable to denial of service via a crafted ZIP file with a manipulated uncompressed size header field. In zipEntry.js line 103, Buffer.alloc(_centralHeader.size) allocates memory based on the declared uncompressed size from the ZIP central directory header without validating it against the actual compressed data size or imposing any upper bound. The size value is read directly from the binary header at entryHeader.js line 266 with no bounds check. An attacker can craft a ~120-byte ZIP file that declares ~4GB uncompressed size, causing a memory allocation amplification ratio of over 33 million to 1. The allocation occurs before CRC validation, so the malicious payload cannot be rejected early. All extraction and read methods are affected: readFile(), readAsText(), extractEntryTo(), extractAllTo(), extractAllToAsync(), test(), and entry.getData(). Any application accepting untrusted ZIP files via adm-zip is vulnerable to immediate process crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39244
- https://github.com/cthackers/adm-zip/issues/568
- https://github.com/cthackers/adm-zip/commit/2450dcf417aa29df49270237d18c5245794da3e2
- https://github.com/cthackers/adm-zip
- https://github.com/cthackers/adm-zip/releases
