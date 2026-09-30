# [M] Hugging Face Smolagents XPath injection vulnerability in the search_item_ctrl_f function

## Summary
Severity: Medium
Advisory: GHSA-8mf9-rmgw-33qc
CVE: CVE-2025-11844
CWE: CWE-643
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-8mf9-rmgw-33qc
Type: github-advisory

## Affected
- PyPI: `smolagents` — affected >=0 <1.22.0

## Details
Hugging Face Smolagents version 1.20.0 contains an XPath injection vulnerability in the search_item_ctrl_f function located in src/smolagents/vision_web_browser.py. The function constructs an XPath query by directly concatenating user-supplied input into the XPath expression without proper sanitization or escaping. This allows an attacker to inject malicious XPath syntax that can alter the intended query logic. The vulnerability enables attackers to bypass search filters, access unintended DOM elements, and disrupt web automation workflows. This can lead to information disclosure, manipulation of AI agent interactions, and compromise the reliability of automated web tasks. The issue is fixed in version 1.22.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11844
- https://github.com/huggingface/smolagents/commit/f570ed5e17999d4cf7d5e79c2830fbaefab8a794
- https://github.com/huggingface/smolagents
- https://huntr.com/bounties/01ab4405-9bca-4b26-b7a3-5ca1863a69b4
