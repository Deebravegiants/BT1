# [H] ALEAPP NQ Vault Artifact Parser Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-40027
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-40027
Type: osv

## Details
ALEAPP (Android Logs Events And Protobuf Parser) through 3.4.0 contains a path traversal vulnerability in the NQ_Vault.py artifact parser that uses attacker-controlled file_name_from values from a database directly as the output filename, allowing arbitrary file writes outside the report output directory. An attacker can embed a path traversal payload such as ../../../outside_written.bin in the database to write files to arbitrary locations, potentially achieving code execution by overwriting executable files or configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40027.json
- https://mobasi.ai/sentinel
- https://nvd.nist.gov/vuln/detail/CVE-2026-40027
- https://www.vulncheck.com/advisories/aleapp-nq-vault-artifact-parser-path-traversal
- https://github.com/abrignoni/aleapp/pull/669
- https://github.com/abrignoni/ALEAPP/commit/0cafd8fe0027663420eb3d0fa821b2d1a713880d
