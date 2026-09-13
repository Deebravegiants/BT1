# [M] LlamaIndex <= 0.12.2 VannaQueryEngine SQL Execution Allows Resource Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2024-58339
Aliases: PYSEC-2026-86
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2024-58339
Type: osv

## Details
LlamaIndex (run-llama/llama_index) versions up to and including 0.12.2 contain an uncontrolled resource consumption vulnerability in the VannaPack VannaQueryEngine implementation. The custom_query() logic generates SQL statements from a user-supplied prompt and executes them via vn.run_sql() without enforcing query execution limits In downstream deployments where untrusted users can supply prompts, an attacker can trigger expensive or unbounded SQL operations that exhaust CPU or memory resources, resulting in a denial-of-service condition. The vulnerable execution path occurs in llama_index/packs/vanna/base.py within custom_query().

## References
- https://www.llamaindex.ai/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58339.json
- https://github.com/run-llama/llama_index
- https://nvd.nist.gov/vuln/detail/CVE-2024-58339
- https://www.vulncheck.com/advisories/llamaindex-vannaqueryengine-sql-execution-allows-resource-exhaustion
- https://huntr.com/bounties/a1d6c30d-fce0-412a-bd22-14e0d4c1fa1f
