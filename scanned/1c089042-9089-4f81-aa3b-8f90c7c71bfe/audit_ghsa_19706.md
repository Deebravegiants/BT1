# [H] Gradio DOS in multipart boundry while uploading the file

## Summary
Severity: High
Advisory: GHSA-5cpq-9538-jm2j
CVE: CVE-2024-8966
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5cpq-9538-jm2j
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0

## Details
A vulnerability in the file upload process of gradio-app/gradio version @gradio/video@0.10.2 allows for a Denial of Service (DoS) attack. An attacker can append a large number of characters to the end of a multipart boundary, causing the system to continuously process each character and issue warnings. This can render Gradio inaccessible for extended periods, disrupting services and causing significant downtime.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8966
- https://github.com/gradio-app/gradio/commit/f1718c47137f9c60240da7afe5e3290aa0f1cb47
- https://github.com/gradio-app/gradio
- https://huntr.com/bounties/7b5932bb-58d1-4e71-b85c-43dc40522ff2
