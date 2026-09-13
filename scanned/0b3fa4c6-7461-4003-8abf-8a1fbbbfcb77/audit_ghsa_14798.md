# [M] code injection vulnerability exists in the huggingface/text-generation-inference repository

## Summary
Severity: Medium
Advisory: GHSA-qq99-p57r-g3v7
CVE: CVE-2024-3924
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-qq99-p57r-g3v7
Type: github-advisory

## Affected
- PyPI: `text-generation` — affected >=0 <2.0.0

## Details
A code injection vulnerability exists in the huggingface/text-generation-inference repository, specifically within the `autodocs.yml` workflow file. The vulnerability arises from the insecure handling of the `github.head_ref` user input, which is used to dynamically construct a command for installing a software package. An attacker can exploit this by forking the repository, creating a branch with a malicious payload as the name, and then opening a pull request to the base repository. Successful exploitation could lead to arbitrary code execution within the context of the GitHub Actions runner. This issue affects versions up to and including v2.0.0 and was fixed in version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3924
- https://github.com/huggingface/text-generation-inference/commit/88702d876383f7200eccf67e28ba00500dc804bb
- https://github.com/huggingface/text-generation-inference
- https://huntr.com/bounties/8af92fc2-0103-4d29-bb28-c3893154c422
