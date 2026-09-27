# [C] Assisted Migration Agent: Path traversal in gzipped tarball handling enables arbitrary file write and remote code execution

## Summary
Severity: Critical
Advisory: GHSA-7j4w-x8x8-5mvg
CVE: CVE-2026-53476
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-7j4w-x8x8-5mvg
Type: github-advisory

## Affected
- Go: `github.com/kubev2v/assisted-migration-agent` — affected >=0 <0.16.0

## Details
A flaw was found in assisted-migration-agent. An unauthenticated attacker, located on the same local area network (LAN), can exploit a path traversal vulnerability. By crafting a specially designed gzipped tarball, the attacker can bypass security checks and write arbitrary files to the system. This could ultimately lead to the execution of unauthorized code on the appliance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53476
- https://github.com/kubev2v/assisted-migration-agent/pull/256
- https://github.com/kubev2v/assisted-migration-agent/commit/bcae0438ad8386321a300413d71c982a11b7b5b7
- https://access.redhat.com/security/cve/CVE-2026-53476
- https://bugzilla.redhat.com/show_bug.cgi?id=2487233
- https://github.com/kubev2v/assisted-migration-agent
