# [C] LlamaIndex <= 0.11.6 BGEM3Index Unsafe Deserialization

## Summary
Severity: Critical
Advisory: CVE-2024-14021
Aliases: PYSEC-2026-85
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2024-14021
Type: osv

## Details
LlamaIndex (run-llama/llama_index) versions up to and including 0.11.6 contain an unsafe deserialization vulnerability in BGEM3Index.load_from_disk() in llama_index/indices/managed/bge_m3/base.py. The function uses pickle.load() to deserialize multi_embed_store.pkl from a user-supplied persist_dir without validation. An attacker who can provide a crafted persist directory containing a malicious pickle file can trigger arbitrary code execution when the victim loads the index from disk.

## References
- https://www.llamaindex.ai/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/14xxx/CVE-2024-14021.json
- https://github.com/run-llama/llama_index
- https://nvd.nist.gov/vuln/detail/CVE-2024-14021
- https://www.vulncheck.com/advisories/llamaindex-bgem3index-unsafe-deserialization
- https://huntr.com/bounties/ab4ceeb4-aa85-4d1c-aaca-4eda1b71fc12
