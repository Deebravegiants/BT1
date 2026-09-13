# [H] Gradio Vulnerable to Denial of Service (DoS) via Crafted HTTP Request

## Summary
Severity: High
Advisory: GHSA-rvgh-pr46-x7gg
CVE: CVE-2024-10624
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-rvgh-pr46-x7gg
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=4.38.0

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability exists in the gradio-app/gradio repository, affecting the gr.Datetime component. The affected version is git commit 98cbcae. The vulnerability arises from the use of a regular expression `^(?:\s*now\s*(?:-\s*(\d+)\s*([dmhs]))?)?\s*$` to process user input. In Python's default regex engine, this regular expression can take polynomial time to match certain crafted inputs. An attacker can exploit this by sending a crafted HTTP request, causing the gradio process to consume 100% CPU and potentially leading to a Denial of Service (DoS) condition on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10624
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/blob/98cbcaef827de7267462ccba180c7b2ffb1e825d/gradio/components/datetime.py#L133-L136
- https://huntr.com/bounties/e8d0b248-8feb-4c23-9ef9-be4d1e868374
