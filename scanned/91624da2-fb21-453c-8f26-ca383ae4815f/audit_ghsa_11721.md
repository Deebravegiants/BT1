# [M] OpenClaw: system.run approval identity mismatch could execute a different binary than displayed

## Summary
Severity: Medium
Advisory: GHSA-hwpq-rrpf-pgcq
CVE: CVE-2026-32065
CWE: CWE-436, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-hwpq-rrpf-pgcq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
`system.run` approvals in OpenClaw used rendered command text as the approval identity while trimming argv token whitespace. Runtime execution still used raw argv. A crafted trailing-space executable token could therefore execute a different binary than what the approver saw.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.24`
- Patched versions: `>= 2026.2.25`

### Impact
This is an approval-integrity bypass that can lead to unexpected command execution under the OpenClaw runtime user when an attacker can influence `command` argv and reuse/obtain a matching approval context.

### Trust Model Note
OpenClaw does not treat adversarial multi-user sharing of one gateway host/config as a supported security boundary. This finding is still valid in supported deployments because it breaks the operator approval boundary itself (approved display command vs executed argv).

### Fix Commit(s)
- `03e689fc89bbecbcd02876a95957ef1ad9caa176`

### Release Process Note
`patched_versions` is pre-set to the release (`2026.2.25`). Advisory published with npm release `2026.2.25`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hwpq-rrpf-pgcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32065
- https://github.com/openclaw/openclaw/commit/03e689fc89bbecbcd02876a95957ef1ad9caa176
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-approval-identity-mismatch-in-system-run-command-execution
