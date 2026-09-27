# [H] Agno session state overwrites between different sessions/users

## Summary
Severity: High
Advisory: GHSA-vw84-hprm-cxmm
CVE: CVE-2025-64168
CWE: CWE-362, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-10-31
Source: https://github.com/advisories/GHSA-vw84-hprm-cxmm
Type: github-advisory

## Affected
- PyPI: `agno` — affected >=2.0.0 <2.2.2

## Details
### Impact
Under certain conditions (under high concurrency), when `session_state` is passed to an Agent or Team during run or arun calls, a race condition can occur, causing a `session_state` to be assigned and persisted to the incorrect session. This may result in user data from one session being exposed to another user.

### Patches
This has been patched in version 2.2.2. Upgrade with `pip install -U agno`.

## References
- https://github.com/agno-agi/agno/security/advisories/GHSA-vw84-hprm-cxmm
- https://nvd.nist.gov/vuln/detail/CVE-2025-64168
- https://github.com/agno-agi/agno
