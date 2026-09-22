# [C] UpSnap - Unauthenticated Initial-Superuser Takeover Chains to Root RCE via wake_cmd

## Summary
Severity: Critical
Advisory: CVE-2026-49819
Aliases: GHSA-w4jr-728f-5jhq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-49819
Type: osv

## Details
UpSnap is a wake on lan web app. Versions 4.4.1 through 5.3.5 are vulnerable to a missing-authentication / privilege-escalation chain in `pb.HandlerInitSuperuser` (`backend/pb/handlers.go:249`), reachable as `POST /api/upsnap/init-superuser`. The vulnerable code lacks any authentication, setup token, IP allow-list, or rate limit and is gated only by a `totalSuperusers > 0` count check — a condition that is false on every fresh install — allowing an unauthenticated network-adjacent attacker to register the initial superuser account, receive a long-lived JWT, and pivot to root remote code execution at `backend/networking/wake.go:43` (`exec.CommandContext(ctx, "/bin/sh", "-c", wake_cmd)`). Version 5.4.0 fixes the issue.

## References
- https://github.com/seriousm4x/UpSnap/releases/tag/5.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49819.json
- https://github.com/seriousm4x/UpSnap/security/advisories/GHSA-w4jr-728f-5jhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49819
