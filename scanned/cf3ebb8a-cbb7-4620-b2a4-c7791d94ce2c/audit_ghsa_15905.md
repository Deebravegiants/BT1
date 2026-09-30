# [M] Gradio's `is_in_or_equal` function may be bypassed

## Summary
Severity: Medium
Advisory: GHSA-77xq-6g77-h274
CVE: CVE-2024-47164
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-77xq-6g77-h274
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.0.0

## Details
### Impact
**What kind of vulnerability is it? Who is impacted?**

This vulnerability relates to the **bypass of directory traversal checks** within the `is_in_or_equal` function. This function, intended to check if a file resides within a given directory, can be bypassed with certain payloads that manipulate file paths using `..` (parent directory) sequences. Attackers could potentially access restricted files if they are able to exploit this flaw, although the difficulty is high. This primarily impacts users relying on Gradio’s blocklist or directory access validation, particularly when handling file uploads.

### Patches
Yes, please upgrade to `gradio>=5.0` to address this issue.

### Workarounds
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

As a workaround, users can manually sanitize and normalize file paths in their Gradio deployment before passing them to the `is_in_or_equal` function. Ensuring that all file paths are properly resolved and absolute can help mitigate the bypass vulnerabilities caused by the improper handling of `..` sequences or malformed paths.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-77xq-6g77-h274
- https://nvd.nist.gov/vuln/detail/CVE-2024-47164
- https://github.com/gradio-app/gradio/commit/08b51590163b306fd874f543f6fcaf23ac7d2646
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-213.yaml
