# [H] Heketi Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-6g56-v9qg-jp92
CVE: CVE-2017-15103
CWE: CWE-20, CWE-78, CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-6g56-v9qg-jp92
Type: github-advisory

## Affected
- Go: `github.com/heketi/heketi` — affected >=0 <5.0.1

## Details
A security-check flaw was found in the way the Heketi 5 server API handled user requests. An authenticated Heketi user could send specially crafted requests to the Heketi server, resulting in remote command execution as the user running Heketi server and possibly privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15103
- https://github.com/heketi/heketi/commit/787bae461b23003a4daa4d1d639016a754cf6b00
- https://access.redhat.com/errata/RHSA-2017:3481
- https://access.redhat.com/security/cve/CVE-2017-15103
- https://bugzilla.redhat.com/show_bug.cgi?id=1510147
- https://github.com/heketi/heketi
- https://github.com/heketi/heketi/releases/tag/v5.0.1
