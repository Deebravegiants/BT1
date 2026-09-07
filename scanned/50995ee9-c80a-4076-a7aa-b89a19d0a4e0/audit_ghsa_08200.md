# [C] KubeVirt has a Link Following vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7jcp-v9w4-wjmg
CVE: CVE-2026-7374
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-7jcp-v9w4-wjmg
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=1.8.0-alpha.0 <1.8.3
- Go: `kubevirt.io/kubevirt` — affected >=1.7.0-alpha.0 <1.7.4
- Go: `kubevirt.io/kubevirt` — affected >=0 <1.6.6

## Details
A flaw was found in KubeVirt's virt-handler component. This vulnerability allows an authenticated OpenShift user with edit permissions in a single namespace to exploit improper symlink validation when connecting to virtual machine console sockets. By replacing the console socket with a symlink to the host's container runtime (CRI-O) socket, an attacker can hijack virt-handler's privileged connection. This enables the attacker to access any Unix socket on the host, potentially leading to full control of the node and the entire cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7374
- https://github.com/kubevirt/kubevirt/pull/17916
- https://github.com/kubevirt/kubevirt/commit/011eef8129e2c21e0ea496f283ee1676009bc757
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-7374.json
- https://github.com/kubevirt/kubevirt
- https://bugzilla.redhat.com/show_bug.cgi?id=2463728
- https://access.redhat.com/security/cve/CVE-2026-7374
- https://access.redhat.com/errata/RHSA-2026:20975
- https://access.redhat.com/errata/RHSA-2026:20890
- https://access.redhat.com/errata/RHSA-2026:20886
- https://access.redhat.com/errata/RHSA-2026:20866
- https://access.redhat.com/errata/RHSA-2026:20825
- https://access.redhat.com/errata/RHSA-2026:20782
- https://access.redhat.com/errata/RHSA-2026:20767
- https://access.redhat.com/errata/RHSA-2026:20763
- https://access.redhat.com/errata/RHSA-2026:20736
- https://access.redhat.com/errata/RHSA-2026:20720
