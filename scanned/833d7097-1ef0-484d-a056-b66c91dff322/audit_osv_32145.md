# [H] .krun_config.json symlink attack creates or overwrites file on the host in crun

## Summary
Severity: High
Advisory: CVE-2025-24965
Aliases: GHSA-f42g-r5jj-qh4j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-24965
Type: osv

## Details
crun is an open source OCI Container Runtime fully written in C. In affected versions A malicious container image could trick the krun handler into escaping the root filesystem, allowing file creation or modification on the host. No special permissions are needed, only the ability for the current user to write to the target file. The problem is fixed in crun 1.20 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/containers/crun/releases/tag/1.20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24965.json
- https://github.com/containers/crun/security/advisories/GHSA-f42g-r5jj-qh4j
- https://nvd.nist.gov/vuln/detail/CVE-2025-24965
- https://github.com/containers/crun/commit/0aec82c2b686f0b1793deed43b46524fe2e8b5a7
