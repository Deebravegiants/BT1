# [H] KubeVirt has a Link Following issue

## Summary
Severity: High
Advisory: GHSA-mpmf-3w4r-qfpf
CVE: CVE-2026-9804
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-mpmf-3w4r-qfpf
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0

## Details
A flaw was found in KubeVirt's virt-exportserver component. An attacker with specific namespace-level access can exploit a path traversal vulnerability in the VMExport directory endpoint. By placing a symbolic link (symlink) within an exported filesystem Persistent Volume Claim (PVC) that points outside its designated mount root, the attacker can read arbitrary files from the exporter pod's filesystem. This leads to information disclosure, potentially exposing sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9804
- https://github.com/kubevirt/kubevirt/commit/6ea563fa94d8ca803f8dd9394cefd8cae36bb0ee
- https://access.redhat.com/errata/RHSA-2026:27903
- https://access.redhat.com/errata/RHSA-2026:27913
- https://access.redhat.com/errata/RHSA-2026:27914
- https://access.redhat.com/errata/RHSA-2026:27983
- https://access.redhat.com/errata/RHSA-2026:28002
- https://access.redhat.com/security/cve/CVE-2026-9804
- https://bugzilla.redhat.com/show_bug.cgi?id=2482487
- https://github.com/kubevirt/kubevirt
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-9804.json
