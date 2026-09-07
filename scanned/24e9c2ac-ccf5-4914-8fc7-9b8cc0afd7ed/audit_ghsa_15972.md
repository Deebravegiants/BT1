# [M] Gradio's CORS origin validation accepts the null origin

## Summary
Severity: Medium
Advisory: GHSA-89v2-pqfv-c5r9
CVE: CVE-2024-47165
CWE: CWE-285, CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-89v2-pqfv-c5r9
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.0.0

## Details
### Impact
**What kind of vulnerability is it? Who is impacted?**

This vulnerability relates to **CORS origin validation accepting a null origin**. When a Gradio server is deployed locally, the `localhost_aliases` variable includes "null" as a valid origin. This allows attackers to make unauthorized requests from sandboxed iframes or other sources with a null origin, potentially leading to data theft, such as user authentication tokens or uploaded files. This impacts users running Gradio locally, especially those using basic authentication.

### Patches
Yes, please upgrade to `gradio>=5.0` to address this issue.

### Workarounds
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

As a workaround, users can manually modify the `localhost_aliases` list in their local Gradio deployment to exclude "null" as a valid origin. By removing this value, the Gradio server will no longer accept requests from sandboxed iframes or sources with a null origin, mitigating the potential for exploitation.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-89v2-pqfv-c5r9
- https://nvd.nist.gov/vuln/detail/CVE-2024-47165
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-214.yaml
