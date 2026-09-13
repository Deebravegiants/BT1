# [M] CRI-O has Potential High Memory Consumption from File Read

## Summary
Severity: Medium
Advisory: GHSA-8f93-j3fx-72f3
CVE: CVE-2025-4437
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-8f93-j3fx-72f3
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0

## Details
There's a vulnerability in the CRI-O application where when container is launched with securityContext.runAsUser specifying a non-existent user, CRI-O attempts to create the user, reading the container's entire /etc/passwd file into memory. If this file is excessively large, it can cause the a high memory consumption leading applications to be killed due to out-of-memory. As a result a denial-of-service can be achieved, possibly disrupting other pods and services running in the same host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4437
- https://access.redhat.com/security/cve/CVE-2025-4437
- https://bugzilla.redhat.com/show_bug.cgi?id=2375084
- https://github.com/cri-o/cri-o
- https://pkg.go.dev/vuln/GO-2025-3897
