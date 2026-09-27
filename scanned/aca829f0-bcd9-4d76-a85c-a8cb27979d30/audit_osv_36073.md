# [M] Improper handling of highly compressed data (data amplification) in CISA Malcolm

## Summary
Severity: Medium
Advisory: CVE-2026-19671
Aliases: CVE-2026-19670, GHSA-f2v6-8cj4-mhr6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-19671
Type: osv

## Details
Malcolm's upload-processing pipeline (scripts/safe-extract.py) enforces entry-count, nesting-depth, and total-uncompressed-byte limits when extracting container archives (zip/tar/rar/7z via libarchive), but those limits are not applied when the uploaded file is a single-stream compressed format (.gz, .bz2, .xz, .lzma, .lz) that isn't a .tar.*-style archive. Any authenticated user permitted to upload PCAP/log files can upload a small, highly compressible file (e.g. a gzip bomb) that decompresses to an effectively unbounded size on disk, exhausting the shared Docker volume used by OpenSearch, Logstash, Arkime, and Zeek, and disrupting the platform for all users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19671.json
- https://github.com/cisagov/Malcolm/security/advisories/GHSA-f2v6-8cj4-mhr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-19671
- https://www.cisa.gov/news-events/ics-advisories/icsa-26-230-01
