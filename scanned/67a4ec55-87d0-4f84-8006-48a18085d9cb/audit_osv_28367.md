# [M] Kohya_ss vulenrable to path injection in `common_gui.py` `add_pre_postfix` function (`GHSL-2024-023`)

## Summary
Severity: Medium
Advisory: CVE-2024-32024
Aliases: GHSA-h9fp-j58h-wwrc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-32024
Type: osv

## Details
Kohya_ss is a GUI for Kohya's Stable Diffusion trainers. Kohya_ss is vulnerable to a path injection in the `common_gui.py` `add_pre_postfix` function. This vulnerability is fixed in 23.1.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32024.json
- https://github.com/bmaltais/kohya_ss/security/advisories/GHSA-h9fp-j58h-wwrc
- https://nvd.nist.gov/vuln/detail/CVE-2024-32024
- https://securitylab.github.com/advisories/GHSL-2024-019_GHSL-2024-024_kohya_ss
- https://github.com/bmaltais/kohya_ss/commit/25bb1303fff21cb5bae17236d53504e85c1866df
