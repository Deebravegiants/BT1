# [C] Gradio allows users to access arbitrary files

## Summary
Severity: Critical
Advisory: GHSA-m842-4qm8-7gpq
CVE: CVE-2024-1728
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-m842-4qm8-7gpq
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.19.2

## Details
### Impact
This vulnerability allows users of Gradio applications that have a public link (such as on Hugging Face Spaces) to access files on the machine hosting the Gradio application. This involves intercepting and modifying the network requests made by the Gradio app to the server. 

### Patches
Yes, the problem has been patched in Gradio version 4.19.2 or higher. We have no knowledge of this exploit being used against users of Gradio applications, but we encourage all users to upgrade to Gradio 4.19.2 or higher.

Fixed in: https://github.com/gradio-app/gradio/commit/16fbe9cd0cffa9f2a824a0165beb43446114eec7
CVE: https://nvd.nist.gov/vuln/detail/CVE-2024-1728

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-m842-4qm8-7gpq
- https://nvd.nist.gov/vuln/detail/CVE-2024-1728
- https://github.com/gradio-app/gradio/commit/16fbe9cd0cffa9f2a824a0165beb43446114eec7
- https://github.com/gradio-app/gradio
- https://huntr.com/bounties/9bb33b71-7995-425d-91cc-2c2a2f2a068a
