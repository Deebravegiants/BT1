# [H] Open Source Social Network (OSSN) Vulnerable to Resource Exhaustion via Malicious Image Processing

## Summary
Severity: High
Advisory: CVE-2026-41309
Aliases: GHSA-72qf-xrcw-fhr2
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41309
Type: osv

## Details
Open Source Social Network (OSSN) is open-source social networking software developed in PHP. Versions prior to 9.0 are vulnerable to resource exhaustion. An attacker can upload a specially crafted image with extreme pixel dimensions (e.g., $10000 \times 10000$ pixels). While the compressed file size on disk may be small, the server attempts to allocate significant memory and CPU cycles during the decompression and resizing process, leading to a Denial of Service (DoS) condition. It is highly recommended to upgrade to OSSN 9.0. This version introduces stricter validation of image dimensions and improved resource management during the processing phase. Those who cannot upgrade immediately can mitigate the risk by adjusting their `php.ini` settings to strictly limit `memory_limit` and `max_execution_time` and/or implementing a client-side and server-side check on image headers to reject files exceeding reasonable pixel dimensions (e.g., $4000 \times 4000$ pixels) before processing begins.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41309.json
- https://github.com/opensource-socialnetwork/opensource-socialnetwork/security/advisories/GHSA-72qf-xrcw-fhr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41309
- https://github.com/opensource-socialnetwork/opensource-socialnetwork/issues/2535
- https://github.com/opensource-socialnetwork/opensource-socialnetwork/commit/12357113b3be189da7f6e429979a464e4f982117
