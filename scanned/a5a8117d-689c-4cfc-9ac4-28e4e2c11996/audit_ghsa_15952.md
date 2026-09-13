# [H] Gradio uses insecure communication between the FRP client and server

## Summary
Severity: High
Advisory: GHSA-279j-x4gx-hfrh
CVE: CVE-2024-47871
CWE: CWE-311
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-279j-x4gx-hfrh
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.0.0

## Details
### Impact  
**What kind of vulnerability is it? Who is impacted?**

This vulnerability involves **insecure communication** between the FRP (Fast Reverse Proxy) client and server when Gradio's `share=True` option is used. HTTPS is not enforced on the connection, allowing attackers to intercept and read files uploaded to the Gradio server, as well as modify responses or data sent between the client and server. This impacts users who are sharing Gradio demos publicly over the internet using `share=True` without proper encryption, exposing sensitive data to potential eavesdroppers.

### Patches  
Yes, please upgrade to `gradio>=5` to address this issue.

### Workarounds  
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

As a workaround, users can avoid using `share=True` in production environments and instead host their Gradio applications on servers with HTTPS enabled to ensure secure communication.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-279j-x4gx-hfrh
- https://nvd.nist.gov/vuln/detail/CVE-2024-47871
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-219.yaml
