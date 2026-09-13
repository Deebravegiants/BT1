# [C] Assisted Migration Agent: Hardcoded insecure Transport Layer Security (TLS) connections during vCenter communication

## Summary
Severity: Critical
Advisory: GHSA-8g5p-jxp9-457c
CVE: CVE-2026-53475
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-8g5p-jxp9-457c
Type: github-advisory

## Affected
- Go: `github.com/kubev2v/assisted-migration-agent` — affected >=0 <0.16.0

## Details
A flaw was found in assisted-migration-agent. The application hardcodes insecure Transport Layer Security (TLS) connections when communicating with vCenter. This vulnerability allows a Man-in-the-Middle (MITM) attacker to intercept and harvest vCenter administrator credentials. This can lead to unauthorized access to vCenter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53475
- https://github.com/kubev2v/assisted-migration-agent/pull/268
- https://github.com/kubev2v/assisted-migration-agent/commit/b940fec9f5032a0801e994054d30e81d64b2942a
- https://access.redhat.com/security/cve/CVE-2026-53475
- https://bugzilla.redhat.com/show_bug.cgi?id=2487232
- https://github.com/kubev2v/assisted-migration-agent
