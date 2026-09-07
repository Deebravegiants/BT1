# [M] Gradio applications running locally vulnerable to 3rd party websites accessing routes and uploading files

## Summary
Severity: Medium
Advisory: GHSA-48cq-79qq-6f7x
CVE: CVE-2024-1727
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-48cq-79qq-6f7x
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.19.2

## Details
### Impact
This CVE covers the ability of 3rd party websites to access routes and upload files to users running Gradio applications locally.  For example, the malicious owners of [www.dontvisitme.com](http://www.dontvisitme.com/) could put a script on their website that uploads a large file to http://localhost:7860/upload and anyone who visits their website and has a Gradio app will now have that large file uploaded on their computer

### Patches
Yes, the problem has been patched in Gradio version 4.19.2 or higher. We have no knowledge of this exploit being used against users of Gradio applications, but we encourage all users to upgrade to Gradio 4.19.2 or higher.

Fixed in: https://github.com/gradio-app/gradio/commit/84802ee6a4806c25287344dce581f9548a99834a
CVE: https://nvd.nist.gov/vuln/detail/CVE-2024-1727

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-48cq-79qq-6f7x
- https://nvd.nist.gov/vuln/detail/CVE-2024-1727
- https://github.com/gradio-app/gradio/pull/7503
- https://github.com/gradio-app/gradio/commit/84802ee6a4806c25287344dce581f9548a99834a
- https://github.com/gradio-app/gradio
- https://huntr.com/bounties/a94d55fb-0770-4cbe-9b20-97a978a2ffff
