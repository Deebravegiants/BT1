# [C] Kohya_ss is vulnerable to a command injection in `git_caption_gui.py` (`GHSL-2024-020`)

## Summary
Severity: Critical
Advisory: CVE-2024-32026
Aliases: GHSA-v5cm-33w8-xrj6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-32026
Type: osv

## Details
Kohya_ss is a GUI for Kohya's Stable Diffusion trainers. Kohya_ss is vulnerable to a command injection in `git_caption_gui.py`. This vulnerability is fixed in 23.1.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32026.json
- https://github.com/bmaltais/kohya_ss/security/advisories/GHSA-v5cm-33w8-xrj6
- https://nvd.nist.gov/vuln/detail/CVE-2024-32026
- https://securitylab.github.com/advisories/GHSL-2024-019_GHSL-2024-024_kohya_ss
- https://github.com/bmaltais/kohya_ss/commit/831af8babeb75faff62bcc6a8c6a4f80354f1ff1
