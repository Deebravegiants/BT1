# [M] Open OnDemand allowlist bypass using symlinks in directory downloads (TOCTOU)

## Summary
Severity: Medium
Advisory: CVE-2025-62724
Aliases: GHSA-vjpg-34px-gjrw
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-62724
Type: osv

## Details
Open OnDemand is an open-source HPC portal. Prior to versions 4.0.8 and 3.1.16, users can craft a "Time of Check to Time of Use" (TOCTOU) attack when downloading zip files to access files outside of the OOD_ALLOWLIST. This vulnerability impacts sites that use the file browser allowlists in all current versions of OOD. However, files accessed are still protected by the UNIX permissions. Open OnDemand versions 4.0.8 and 3.1.16 have been patched for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62724.json
- https://github.com/OSC/ondemand/security/advisories/GHSA-vjpg-34px-gjrw
- https://nvd.nist.gov/vuln/detail/CVE-2025-62724
