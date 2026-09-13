# [C] Flatpak has a complete sandbox escape leading to host file access and code execution in the host context

## Summary
Severity: Critical
Advisory: CVE-2026-34078
Aliases: GHSA-cc2q-qc34-jprg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-34078
Type: osv

## Details
Flatpak is a Linux application sandboxing and distribution framework. Prior to 1.16.4, the Flatpak portal accepts paths in the sandbox-expose options which can be app-controlled symlinks pointing at arbitrary paths. Flatpak run mounts the resolved host path in the sandbox. This gives apps access to all host files and can be used as a primitive to gain code execution in the host context. This vulnerability is fixed in 1.16.4.

## References
- http://www.openwall.com/lists/oss-security/2026/04/09/8
- http://www.openwall.com/lists/oss-security/2026/04/10/14
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34078.json
- https://access.redhat.com/errata/RHSA-2026:21755
- https://access.redhat.com/errata/RHSA-2026:21756
- https://access.redhat.com/errata/RHSA-2026:21757
- https://access.redhat.com/errata/RHSA-2026:23417
- https://access.redhat.com/errata/RHSA-2026:23418
- https://access.redhat.com/errata/RHSA-2026:23419
- https://access.redhat.com/errata/RHSA-2026:23420
- https://access.redhat.com/errata/RHSA-2026:25068
- https://access.redhat.com/errata/RHSA-2026:25381
- https://access.redhat.com/errata/RHSA-2026:30901
- https://access.redhat.com/errata/RHSA-2026:35843
- https://access.redhat.com/security/cve/CVE-2026-34078
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34078.json
- https://github.com/flatpak/flatpak/security/advisories/GHSA-cc2q-qc34-jprg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34078
- https://bugzilla.redhat.com/show_bug.cgi?id=2456276
