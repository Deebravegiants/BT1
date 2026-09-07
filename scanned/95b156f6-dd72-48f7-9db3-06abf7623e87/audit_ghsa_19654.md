# [M] XPixelGroup BasicSR Command Injection

## Summary
Severity: Medium
Advisory: GHSA-86w8-vhw6-q9qq
CVE: CVE-2024-27763
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-86w8-vhw6-q9qq
Type: github-advisory

## Affected
- PyPI: `basicsr` — affected >=0

## Details
XPixelGroup BasicSR through 1.4.2 might locally allow code execution in contrived situations where "scontrol show hostname" is executed in the presence of a crafted SLURM_NODELIST environment variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27763
- https://gist.github.com/aydinnyunus/40e1d8a3b529261ae654ff4891f1e192
- https://github.com/XPixelGroup/BasicSR
- https://github.com/XPixelGroup/BasicSR/blob/master/basicsr/utils/dist_util.py#L44
