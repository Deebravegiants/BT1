# [H] Gradio makes the `/file` secure against file traversal and server-side request forgery attacks

## Summary
Severity: High
Advisory: GHSA-6qm2-wpxq-7qh2
CVE: CVE-2023-51449
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-6qm2-wpxq-7qh2
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.11.0

## Details
Older versions of `gradio` contained a vulnerability in the `/file` route which made them susceptible to file traversal attacks in which an attacker could access arbitrary files on a machine running a Gradio app with a public URL (e.g. if the demo was created with `share=True`, or on Hugging Face Spaces) if they knew the path of files to look for. 

This was not possible through regular URLs passed into a browser, but it was possible through the use of programmatic tools such as `curl` with the `--pass-as-is` flag. 

Furthermore,  the `/file` route in Gradio apps also contained a vulnerability that made it possible to use it for SSRF attacks.

Both of these vulnerabilities have been fixed in `gradio==4.11.0`

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-6qm2-wpxq-7qh2
- https://nvd.nist.gov/vuln/detail/CVE-2023-51449
- https://github.com/gradio-app/gradio/commit/1b9d4234d6c25ef250d882c7b90e1f4039ed2d76
- https://github.com/gradio-app/gradio/commit/7ba8c5da45b004edd12c0460be9222f5b5f5f055
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2023-249.yaml
