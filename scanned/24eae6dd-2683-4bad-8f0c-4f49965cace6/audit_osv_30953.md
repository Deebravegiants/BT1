# [H] drm/amd/display: Adding array index check to prevent memory corruption

## Summary
Severity: High
Advisory: CVE-2024-56784
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56784
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Adding array index check to prevent memory corruption

[Why & How]
Array indices out of bound caused memory corruption. Adding checks to
ensure that array index stays in bound.

## References
- https://git.kernel.org/stable/c/2c437d9a0b496168e1a1defd17b531f0a526dbe9
- https://git.kernel.org/stable/c/dff526dc3e27f5484f5ba11471b9fbbe681467f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56784.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56784
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
