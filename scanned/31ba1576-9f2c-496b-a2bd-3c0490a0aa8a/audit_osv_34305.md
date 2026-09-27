# [C] Airlink's Daemon Symlink Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-57802
Aliases: GHSA-hrfv-wm8p-mg8m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-57802
Type: osv

## Details
Airlink's Daemon interfaces with Docker and the Panel to provide secure access for controlling instances via the Panel. In version 1.0.0, an attacker with access to the affected container can create symbolic links inside the mounted directory (/app/data). Because the container bind-mounts an arbitrary host path, these symlinks can point to sensitive locations on the host filesystem. When the application or other processes follow these symlinks, the attacker can gain unauthorized read access to host files outside the container. This issue has been patched in version 1.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57802.json
- https://github.com/airlinklabs/daemon/security/advisories/GHSA-hrfv-wm8p-mg8m
- https://nvd.nist.gov/vuln/detail/CVE-2025-57802
- https://github.com/airlinklabs/daemon/commit/5e6222dd9eec6d7cb0876b12507e3d6011797693
