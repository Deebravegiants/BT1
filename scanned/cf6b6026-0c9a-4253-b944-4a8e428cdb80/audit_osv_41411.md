# [M] Zeek < 8.0.9 Uncontrolled Memory Consumption DoS via FTP Analyzer

## Summary
Severity: Medium
Advisory: CVE-2026-60108
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-60108
Type: osv

## Details
Zeek before 8.0.9 contains an uncontrolled memory consumption vulnerability in the FTP analyzer that allows unauthenticated remote attackers to cause process termination by sending a crafted FTP control session negotiating AUTH GSSAPI followed by a large ADAT control line. Attackers can exploit the NVT_Analyzer component's lack of a maximum line length check, causing it to continuously double its internal buffer without bounds during base64 decoding of an attacker-controlled ADAT token, resulting in denial of service of the Zeek sensor.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60108.json
- https://github.com/zeek/zeek/releases/tag/v8.0.9
- https://nvd.nist.gov/vuln/detail/CVE-2026-60108
- https://www.vulncheck.com/advisories/zeek-uncontrolled-memory-consumption-dos-via-ftp-analyzer
- https://github.com/zeek/zeek/commit/93ff6950a90cfa9d00c1062cde429313a0402a01
- https://github.com/zeek/zeek
