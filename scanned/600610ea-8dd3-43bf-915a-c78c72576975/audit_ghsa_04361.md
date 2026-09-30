# [M] go.qbee.io/transport: Symlink-chain path traversal in tar extraction (one level outside destination)

## Summary
Severity: Medium
Advisory: GHSA-f9m7-vc86-p6jj
CVE: CVE-2026-55828
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-f9m7-vc86-p6jj
Type: github-advisory

## Affected
- Go: `go.qbee.io/transport` — affected >=0 <1.26.25

## Details
### Impact

The go.qbee.io/transport library is affected by a symlink-chain path traversal vulnerability in its extractTar routine. The library's path validation is strictly lexical and fails to account for on-disk symlinks created earlier in the extraction process. Consequently, a crafted tar archive can be used to write or overwrite files one directory level above the intended extraction path. In the case of qbee-agent, which runs with root privileges, this vulnerability permits a root-privileged file write outside the intended destination.

### Patches

The issue has been addressed in version v1.26.25

## References
- https://github.com/qbee-io/transport/security/advisories/GHSA-f9m7-vc86-p6jj
- https://github.com/qbee-io/transport
