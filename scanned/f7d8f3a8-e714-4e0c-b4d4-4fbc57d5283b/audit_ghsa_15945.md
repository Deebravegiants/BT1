# [M] Gradio has an XSS on every Gradio server via upload of HTML files, JS files, or SVG files

## Summary
Severity: Medium
Advisory: GHSA-gvv6-33j7-884g
CVE: CVE-2024-47872
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-gvv6-33j7-884g
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.0.0

## Details
### Impact  
**What kind of vulnerability is it? Who is impacted?**

This vulnerability involves **Cross-Site Scripting (XSS)** on any Gradio server that allows file uploads. Authenticated users can upload files such as HTML, JavaScript, or SVG files containing malicious scripts. When other users download or view these files, the scripts will execute in their browser, allowing attackers to perform unauthorized actions or steal sensitive information from their sessions. This impacts any Gradio server that allows file uploads, particularly those using components that process or display user-uploaded files.

### Patches  
Yes, please upgrade to `gradio>=5` to address this issue.

### Workarounds  
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

As a workaround, users can restrict the types of files that can be uploaded to the Gradio server by limiting uploads to non-executable file types such as images or text. Additionally, developers can implement server-side validation to sanitize uploaded files, ensuring that HTML, JavaScript, and SVG files are properly handled or rejected before being stored or displayed to users.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-gvv6-33j7-884g
- https://nvd.nist.gov/vuln/detail/CVE-2024-47872
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-220.yaml
