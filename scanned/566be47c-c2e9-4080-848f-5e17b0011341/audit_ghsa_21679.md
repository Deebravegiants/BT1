# [M] Incorrect Permission Assignment for Critical Resource in CRI-O

## Summary
Severity: Medium
Advisory: GHSA-jqmc-79gx-7g8p
CVE: CVE-2022-0532
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-jqmc-79gx-7g8p
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.23.1

## Details
An incorrect sysctls validation vulnerability was found in CRI-O 1.18 and earlier. The sysctls from the list of "safe" sysctls specified for the cluster will be applied to the host if an attacker is able to create a pod with a hostIPC and hostNetwork kernel namespace.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0532
- https://github.com/cri-o/cri-o/pull/5610
- https://bugzilla.redhat.com/show_bug.cgi?id=2051730
- https://github.com/cri-o/cri-o
- https://github.com/cri-o/cri-o/releases/tag/v1.23.1
- https://kubernetes.io/docs/tasks/administer-cluster/sysctl-cluster/#enabling-unsafe-sysctls
