# [M] gradio Server Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3gf9-wv65-gwh9
CVE: CVE-2024-48052
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-05
Source: https://github.com/advisories/GHSA-3gf9-wv65-gwh9
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0

## Details
In gradio <=4.42.0, the gr.DownloadButton function has a hidden server-side request forgery (SSRF) vulnerability. The reason is that within the save_url_to_cache function, there are no restrictions on the URL, which allows access to local target resources. This can lead to the download of local resources and sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48052
- https://gist.github.com/AfterSnows/45ffc23797f9127e00755376cc610e12
- https://github.com/gradio-app/gradio
- https://rumbling-slice-eb0.notion.site/FULL-SSRF-in-gr-DownloadButton-in-gradio-app-gradio-870b21e0908b48cbafd914719ac1a4e6?pvs=4
