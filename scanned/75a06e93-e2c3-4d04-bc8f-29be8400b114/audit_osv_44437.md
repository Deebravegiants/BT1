# [M] gpt-crawler Arbitrary File Write via outputFileName Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-82286
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82286
Type: osv

## Details
gpt-crawler through 1.5.1 fails to validate the outputFileName parameter in the POST /crawl endpoint, allowing unauthenticated attackers to write arbitrary files to any filesystem path. Attackers can supply absolute paths or parent-directory segments to overwrite existing files with content sourced from attacker-controlled URLs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82286.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82286
- https://www.vulncheck.com/advisories/gpt-crawler-arbitrary-file-write-via-outputfilename-parameter
- https://github.com/BuilderIO/gpt-crawler/issues/418
- https://github.com/BuilderIO/gpt-crawler
- https://github.com/BuilderIO/gpt-crawler/blob/d2245d66a5ad60bf227a55c849135394cbecc9b5/src/config.ts
- https://github.com/BuilderIO/gpt-crawler/blob/d2245d66a5ad60bf227a55c849135394cbecc9b5/src/core.ts
