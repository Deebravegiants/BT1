# [M] Regular Expression Denial of Service (ReDoS) in huggingface/transformers

## Summary
Severity: Medium
Advisory: CVE-2024-12720
Aliases: GHSA-6rvg-6v2m-4j46, PYSEC-2026-1982
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12720
Type: osv

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability was identified in the huggingface/transformers library, specifically in the file tokenization_nougat_fast.py. The vulnerability occurs in the post_process_single() function, where a regular expression processes specially crafted input. The issue stems from the regex exhibiting exponential time complexity under certain conditions, leading to excessive backtracking. This can result in significantly high CPU usage and potential application downtime, effectively creating a Denial of Service (DoS) scenario. The affected version is v4.46.3 (latest).

## References
- https://huntr.com/bounties/4bed1214-7835-4252-a853-22bbad891f98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12720.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12720
- https://github.com/huggingface/transformers/commit/deac971c469bcbb182c2e52da0b82fb3bf54cccf
