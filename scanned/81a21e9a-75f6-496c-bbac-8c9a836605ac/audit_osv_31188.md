# [M] LangChain <= 0.3.1 MRKLOutputParser ReDoS

## Summary
Severity: Medium
Advisory: CVE-2024-58340
Aliases: PYSEC-2026-75
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2024-58340
Type: osv

## Details
LangChain versions up to and including 0.3.1 contain a regular expression denial-of-service (ReDoS) vulnerability in the MRKLOutputParser.parse() method (libs/langchain/langchain/agents/mrkl/output_parser.py). The parser applies a backtracking-prone regular expression when extracting tool actions from model output. An attacker who can supply or influence the parsed text (for example via prompt injection in downstream applications that pass LLM output directly into MRKLOutputParser.parse()) can trigger excessive CPU consumption by providing a crafted payload, causing significant parsing delays and a denial-of-service condition.

## References
- https://www.langchain.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58340.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58340
- https://www.vulncheck.com/advisories/langchain-mrkloutputparser-redos
- https://github.com/langchain-ai/langchain
- https://huntr.com/bounties/e7ece02c-d4bb-4166-8e08-6baf4f8845bb
