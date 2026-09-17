# [C] CVE-2021-47748

## Summary
Severity: Critical
Advisory: CVE-2021-47748
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2021-47748
Type: osv

## Details
Hasura GraphQL 1.3.3 contains a remote code execution vulnerability that allows attackers to execute arbitrary shell commands through SQL query manipulation. Attackers can inject commands into the run_sql endpoint by crafting malicious GraphQL queries that execute system commands through PostgreSQL's COPY FROM PROGRAM functionality.

## References
- https://www.vulncheck.com/advisories/hasura-graphql-remote-code-execution
- https://github.com/hasura/graphql-engine
- https://www.exploit-db.com/exploits/49802
