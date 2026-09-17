# [C] n8n before 1.123.69 Arbitrary File Read and Write via Snowflake

## Summary
Severity: Critical
Advisory: CVE-2026-77080
Aliases: GHSA-r4j2-j3wm-q689
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77080
Type: osv

## Details
n8n before 1.123.69, 2.x before 2.33.4, and 2.34.x before 2.34.1 contain an arbitrary file read and write vulnerability in the Snowflake node, which passes free-form Execute Query input, including client-side commands, directly to the Snowflake SDK without applying n8n's file-access restrictions. An authenticated user with usable Snowflake credentials can upload a local file from the n8n host or overwrite an existing file with a staged one.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77080.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-r4j2-j3wm-q689
- https://nvd.nist.gov/vuln/detail/CVE-2026-77080
- https://www.vulncheck.com/advisories/n8n-before-arbitrary-file-read-and-write-via-snowflake
