# [C] Kohya_ss is vulnerable to a command injection in `finetune_gui.py` (`GHSL-2024-022`)

## Summary
Severity: Critical
Advisory: CVE-2024-32027
Aliases: GHSA-8h78-3vqm-xw83
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-32027
Type: osv

## Details
Kohya_ss is a GUI for Kohya's Stable Diffusion trainers. Kohya_ss v22.6.1 is vulnerable to command injection in `finetune_gui.py` This vulnerability is fixed in 23.1.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32027.json
- https://github.com/bmaltais/kohya_ss/security/advisories/GHSA-8h78-3vqm-xw83
- https://nvd.nist.gov/vuln/detail/CVE-2024-32027
- https://securitylab.github.com/advisories/GHSL-2024-019_GHSL-2024-024_kohya_ss
- https://github.com/bmaltais/kohya_ss/commit/831af8babeb75faff62bcc6a8c6a4f80354f1ff1
