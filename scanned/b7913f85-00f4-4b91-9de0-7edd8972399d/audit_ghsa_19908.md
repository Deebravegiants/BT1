# [H] Gradio Vulnerable to Arbitrary File Deletion

## Summary
Severity: High
Advisory: GHSA-pgfv-gvc5-prfg
CVE: CVE-2024-10648
CWE: CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-pgfv-gvc5-prfg
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=4.0.0

## Details
A path traversal vulnerability exists in the Gradio Audio component of gradio-app/gradio, as of version git 98cbcae. This vulnerability allows an attacker to control the format of the audio file, leading to arbitrary file content deletion. By manipulating the output format, an attacker can reset any file to an empty file, causing a denial of service (DOS) on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10648
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/blame/98cbcaef827de7267462ccba180c7b2ffb1e825d/gradio/processing_utils.py#L234
- https://huntr.com/bounties/667d664d-8189-458c-8ed7-483fe8f33c76
