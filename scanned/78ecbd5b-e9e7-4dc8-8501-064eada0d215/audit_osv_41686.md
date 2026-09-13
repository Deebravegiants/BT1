# [M] CVE-2026-63252

## Summary
Severity: Medium
Advisory: CVE-2026-63252
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-63252
Type: osv

## Details
In Eclipse Milo versions 0.6.0 through 1.1.4, UASC server transport handlers fail to release retained partial message chunks when a channel disconnects, allowing a remote unauthenticated client to exhaust pooled direct memory by repeatedly sending incomplete chunks and disconnecting, potentially terminating the server.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/179
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63252.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63252
- https://github.com/eclipse-milo/milo/commit/459715793ec54b0f33367a14f94264500a0d872b
