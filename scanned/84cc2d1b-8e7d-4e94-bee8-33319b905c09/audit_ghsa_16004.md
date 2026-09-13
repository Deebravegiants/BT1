# [M] Link Following in github.com/containers/common

## Summary
Severity: Medium
Advisory: GHSA-mc76-5925-c5p6
CVE: CVE-2024-9341
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-mc76-5925-c5p6
Type: github-advisory

## Affected
- Go: `github.com/containers/common` — affected >=0 <0.60.4

## Details
A flaw was found in Go. When FIPS mode is enabled on a system, container runtimes may incorrectly handle certain file paths due to improper validation in the containers/common Go library. This flaw allows an attacker to exploit symbolic links and trick the system into mounting sensitive host directories inside a container. This issue also allows attackers to access critical host files, bypassing the intended isolation between containers and the host system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9341
- https://github.com/containers/common/commit/e7db06585c32e1a782c1d9aa3b71ccd708f5e23f
- https://github.com/containers/common/blob/384f77532f67afc8a73d8e0c4adb0d195df57714/pkg/subscriptions/subscriptions.go#L349
- https://github.com/containers/common/blob/384f77532f67afc8a73d8e0c4adb0d195df57714/pkg/subscriptions/subscriptions.go#L169
- https://github.com/containers/common
- https://bugzilla.redhat.com/show_bug.cgi?id=2315691
- https://access.redhat.com/security/cve/CVE-2024-9341
- https://access.redhat.com/errata/RHSA-2024:9459
- https://access.redhat.com/errata/RHSA-2024:9454
- https://access.redhat.com/errata/RHSA-2024:8846
- https://access.redhat.com/errata/RHSA-2024:8694
- https://access.redhat.com/errata/RHSA-2024:8690
- https://access.redhat.com/errata/RHSA-2024:8428
- https://access.redhat.com/errata/RHSA-2024:8263
- https://access.redhat.com/errata/RHSA-2024:8238
- https://access.redhat.com/errata/RHSA-2024:8112
- https://access.redhat.com/errata/RHSA-2024:8039
- https://access.redhat.com/errata/RHSA-2024:7925
- https://access.redhat.com/errata/RHSA-2024:10818
- https://access.redhat.com/errata/RHSA-2024:10147
