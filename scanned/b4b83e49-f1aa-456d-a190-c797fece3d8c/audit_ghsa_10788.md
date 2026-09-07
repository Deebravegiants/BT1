# [H] Neko has a Self-service Privilege Escalation for Authenticated Users

## Summary
Severity: High
Advisory: GHSA-2gw9-c2r2-f5qf
CVE: CVE-2026-39386
CWE: CWE-20, CWE-269, CWE-284, CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-2gw9-c2r2-f5qf
Type: github-advisory

## Affected
- Go: `github.com/m1k1o/neko/server` — affected >=3.0.0 <3.0.11
- Go: `github.com/m1k1o/neko/server` — affected >=0.0.0-20250322225643-212bf8a60756 <0.0.0-20260406184107-c54bcf1ee211

## Details
### Impact

Any authenticated user can immediately obtain full administrative control of the entire Neko instance (member management, room settings, broadcast control, session termination, etc.). This results in a complete compromise of the instance.

### Patches

The vulnerability has been patched in the following releases:

- [v3.0.11](https://github.com/m1k1o/neko/releases/tag/v3.0.11) (backport release)
- [v3.1.2](https://github.com/m1k1o/neko/releases/tag/v3.1.2) (latest stable release)

Users should upgrade to [v3.0.11](https://github.com/m1k1o/neko/releases/tag/v3.0.11) or later (for the 3.0 branch) or [v3.1.2](https://github.com/m1k1o/neko/releases/tag/v3.1.2) or later.

### Workarounds

If upgrading is not immediately possible, the following mitigations can reduce risk:

- Restrict access to trusted users only (avoid granting accounts to untrusted parties)
- Run the instance only when needed; avoid leaving it continuously exposed
- Disable or restrict access to the `/api/profile` endpoint if feasible
- Monitor for suspicious privilege changes or unexpected administrative actions

Note: These are temporary mitigations and do not fully eliminate the vulnerability. Upgrading is strongly recommended.

### Credits
Neko thanks @blitzkrieg-patch for responsibly disclosing this vulnerability and reaching out directly. This contribution helped strengthen the project, and the whole community benefits from it.

## References
- https://github.com/m1k1o/neko/security/advisories/GHSA-2gw9-c2r2-f5qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-39386
- https://github.com/m1k1o/neko/commit/6b561feb9016badea99ae7305091c0ff55e1d114
- https://github.com/m1k1o/neko/commit/c54bcf1ee211e28104a2bb6db59583a39c4a4d6e
- https://github.com/m1k1o/neko
- https://github.com/m1k1o/neko/releases/tag/v3.0.11
- https://github.com/m1k1o/neko/releases/tag/v3.1.2
