# [M] Gradio has a one-level read path traversal in `/custom_component`

## Summary
Severity: Medium
Advisory: GHSA-37qc-qgx6-9xjv
CVE: CVE-2024-47166
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-37qc-qgx6-9xjv
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.44.0

## Details
### Impact  
**What kind of vulnerability is it? Who is impacted?**

This vulnerability involves a **one-level read path traversal** in the `/custom_component` endpoint. Attackers can exploit this flaw to access and leak source code from custom Gradio components by manipulating the file path in the request. Although the traversal is limited to a single directory level, it could expose proprietary or sensitive code that developers intended to keep private. This impacts users who have developed custom Gradio components and are hosting them on publicly accessible servers.

### Patches  
Yes, please upgrade to `gradio>=4.44` to address this issue.

### Workarounds  
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

As a workaround, developers can sanitize the file paths and ensure that components are not stored in publicly accessible directories.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-37qc-qgx6-9xjv
- https://nvd.nist.gov/vuln/detail/CVE-2024-47166
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-197.yaml
