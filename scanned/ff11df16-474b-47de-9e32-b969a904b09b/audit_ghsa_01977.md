# [M] Improper Input Validation

## Summary
Severity: Medium
Advisory: GHSA-57v4-m9jx-mh8r
CVE: CVE-2021-3499
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-57v4-m9jx-mh8r
Type: github-advisory

## Affected
- Go: `github.com/ovn-org/ovn-kubernetes` — affected >=0

## Details
A vulnerability was found in OVN Kubernetes in versions up to and including 0.3.0 where the Egress Firewall does not reliably apply firewall rules when there is multiple DNS rules. It could lead to potentially lose of confidentiality, integrity or availability of a service

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3499
- https://github.com/ovn-org/ovn-kubernetes/pull/2169
- https://access.redhat.com/errata/RHBA-2021:1550
- https://access.redhat.com/security/cve/CVE-2021-3499
- https://bugzilla.redhat.com/show_bug.cgi?id=1949188
