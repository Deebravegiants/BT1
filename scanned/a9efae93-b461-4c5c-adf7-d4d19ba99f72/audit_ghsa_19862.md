# [H] Gradio Vulnerable to Denial of Service (DoS) via Crafted Zip Bomb

## Summary
Severity: High
Advisory: GHSA-7xmc-vhjp-qv5q
CVE: CVE-2024-10569
CWE: CWE-475
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-7xmc-vhjp-qv5q
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=4.0.0

## Details
A vulnerability in the dataframe component of gradio-app/gradio (version git 98cbcae) allows for a zip bomb attack. The component uses pd.read_csv to process input values, which can accept compressed files. An attacker can exploit this by uploading a maliciously crafted zip bomb, leading to a server crash and causing a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10569
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/blob/98cbcaef827de7267462ccba180c7b2ffb1e825d/gradio/components/dataframe.py#L263
- https://huntr.com/bounties/7192bcbb-08a3-4d22-a321-9c6d19dbfc74
