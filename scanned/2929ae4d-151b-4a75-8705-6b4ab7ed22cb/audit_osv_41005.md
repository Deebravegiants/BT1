# [M] OpenHarness - Cross-Session Disclosure via /resume and /summary Commands

## Summary
Severity: Medium
Advisory: CVE-2026-56695
Aliases: GHSA-399c-3gm2-p29v, PYSEC-2026-3881
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56695
Type: osv

## Details
OpenHarness ohmo gateway /resume and /summary slash commands default remote_invocable to True, allowing admitted remote senders to enumerate and load arbitrary session snapshots by ID. Attackers can exploit this to access victim snapshots containing private prompts, credentials, tool output, and file paths via shared gateway channels.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56695
- https://www.vulncheck.com/advisories/openharness-cross-session-disclosure-via-resume-and-summary-commands
- https://github.com/HKUDS/OpenHarness/pull/276
- https://github.com/HKUDS/OpenHarness/commit/92e298852c9b9c8c2266236292073623418c640a
- https://github.com/HKUDS/OpenHarness
