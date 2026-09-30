# [C] Storage volume cross-project move and snapshot restore bypass project disk limits

## Summary
Severity: Critical
Advisory: CVE-2026-63299
Aliases: GHSA-5h78-p252-989h
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63299
Type: osv

## Details
An authorization bypass vulnerability in LXD allows an authenticated user to bypass project-level disk and volume limits. Two related code paths fail to verify resource limits during volume operations: the storagePoolVolumeTypePostMove function omits the limits.AllowVolumeCreation check before moving a volume across projects, and volume snapshot restore operations skip the AllowVolumeUpdate check when the configuration is nil (Config == nil). An attacker can exploit these flaws to allocate storage resources that exceed the administrative limits configured for a project.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63299.json
- https://github.com/canonical/lxd/security/advisories/GHSA-5h78-p252-989h
- https://nvd.nist.gov/vuln/detail/CVE-2026-63299
- https://github.com/canonical/lxd
