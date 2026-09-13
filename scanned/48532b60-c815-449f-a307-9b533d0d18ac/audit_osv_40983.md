# [H] Authenticated Remote Code Execution via Arbitrary NDJSON Error Log Path in MISP

## Summary
Severity: High
Advisory: CVE-2026-56446
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56446
Type: osv

## Details
MISP allowed a site administrator to configure an arbitrary filesystem path for the NDJSON error log used by JsonLogTool. Because log entries can include attacker-controlled content, an authenticated attacker with site administrator privileges could direct log output to a PHP file in a web-accessible directory and inject PHP code through logged data. Accessing the resulting file could lead to remote code execution with the privileges of the web server process.

The fix restricts log destinations to existing directories beneath APP/tmp/logs or /var/log, requires absolute paths, rejects stream wrappers and traversal-related input, and limits filenames to .log or .ndjson extensions while disallowing executable extension segments.

## References
- https://github.com/MISP/MISP/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56446
- https://github.com/MISP/MISP/commit/9600d486ccfc98388e13897fd954350cebac5fb0
