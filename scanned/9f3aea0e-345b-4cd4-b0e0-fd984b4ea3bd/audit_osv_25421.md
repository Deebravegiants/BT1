# [C] CVE-2023-36281

## Summary
Severity: Critical
Advisory: CVE-2023-36281
Aliases: GHSA-7gfq-f96f-g85j, PYSEC-2023-151
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2023-36281
Type: osv

## Details
An issue in langchain v.0.0.171 allows a remote attacker to execute arbitrary code via a JSON file to load_prompt. This is related to __subclasses__ or a template.

## References
- https://aisec.today/LangChain-2e6244a313dd46139c5ef28cbcab9e55
- https://github.com/langchain-ai/langchain/releases/tag/v0.0.312
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36281.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-36281
- https://github.com/hwchase17/langchain/issues/4394
