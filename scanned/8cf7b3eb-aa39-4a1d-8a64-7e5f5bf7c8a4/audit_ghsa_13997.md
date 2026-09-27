# [M] transformers has Insecure Temporary File

## Summary
Severity: Medium
Advisory: GHSA-282v-666c-3fvg
CVE: CVE-2023-2800
CWE: CWE-377
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-18
Source: https://github.com/advisories/GHSA-282v-666c-3fvg
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <4.30.0

## Details
Insecure Temporary File in GitHub repository huggingface/transformers 4.29.2 and prior. A fix is available at commit 80ca92470938bbcc348e2d9cf4734c7c25cb1c43 and has been released as part of version 4.30.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2800
- https://github.com/huggingface/transformers/pull/23372
- https://github.com/huggingface/transformers/commit/80ca92470938bbcc348e2d9cf4734c7c25cb1c43
- https://github.com/huggingface/transformers
- https://github.com/pypa/advisory-database/tree/main/vulns/transformers/PYSEC-2023-299.yaml
- https://huntr.dev/bounties/a3867b4e-6701-4418-8c20-3c6e7084a44a
