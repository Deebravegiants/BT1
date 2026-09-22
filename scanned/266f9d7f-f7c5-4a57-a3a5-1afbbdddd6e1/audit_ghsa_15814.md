# [M] Gradio has several components with post-process steps allow arbitrary file leaks

## Summary
Severity: Medium
Advisory: GHSA-4q3c-cj7g-jcwf
CVE: CVE-2024-47868
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-4q3c-cj7g-jcwf
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.0.0

## Details
### Impact
**What kind of vulnerability is it? Who is impacted?**

This is a **data validation vulnerability** affecting several Gradio components, which allows arbitrary file leaks through the post-processing step. Attackers can exploit these components by crafting requests that bypass expected input constraints. This issue could lead to sensitive files being exposed to unauthorized users, especially when combined with other vulnerabilities, such as issue TOB-GRADIO-15. The components most at risk are those that return or handle file data.

### Vulnerable Components:
1. **String to FileData:** DownloadButton, Audio, ImageEditor, Video, Model3D, File, UploadButton.
2. **Complex data to FileData:** Chatbot, MultimodalTextbox.
3. **Direct file read in preprocess:** Code.
4. **Dictionary converted to FileData:** ParamViewer, Dataset.

### Exploit Scenarios:
1. A developer creates a Dropdown list that passes values to a DownloadButton. An attacker bypasses the allowed inputs, sends an arbitrary file path (like `/etc/passwd`), and downloads sensitive files.
2. An attacker crafts a malicious payload in a ParamViewer component, leaking sensitive files from a server through the arbitrary file leak.

### Patches
Yes, the issue has been resolved in `gradio>5.0`. Upgrading to the latest version will mitigate this vulnerability.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-4q3c-cj7g-jcwf
- https://nvd.nist.gov/vuln/detail/CVE-2024-47868
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-217.yaml
