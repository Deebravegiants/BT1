# [M] Kohya_ss vulnerable to path injection in `common_gui.py` `find_and_replace` function (`GHSL-2024-024`)

## Summary
Severity: Medium
Advisory: CVE-2024-32023
Aliases: GHSA-p945-7qm7-7j53
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-32023
Type: osv

## Details
Kohya_ss is a GUI for Kohya's Stable Diffusion trainers. Kohya_ss is vulnerable to a path injection in the `common_gui.py` `find_and_replace` function. This vulnerability is fixed in 23.1.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32023.json
- https://github.com/bmaltais/kohya_ss/security/advisories/GHSA-p945-7qm7-7j53
- https://nvd.nist.gov/vuln/detail/CVE-2024-32023
- https://securitylab.github.com/advisories/GHSL-2024-019_GHSL-2024-024_kohya_ss
- https://github.com/bmaltais/kohya_ss/commit/8bc67a7467f8366db1a4b9b3b14525ec763f1650
