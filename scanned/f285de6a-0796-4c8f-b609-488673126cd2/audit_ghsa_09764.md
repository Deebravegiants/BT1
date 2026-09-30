# [M] OpenClaw: Sender policy bypass in host media attachment reads allows unauthorized local file disclosure

## Summary
Severity: Medium
Advisory: GHSA-jhpv-5j76-m56h
CVE: CVE-2026-42438
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-jhpv-5j76-m56h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.9 <2026.4.10

## Details
## Summary

OpenClaw's outbound host-media attachment read helper could enable host-local file reads based on global or agent-level read access without also honoring sender and group-scoped tool policy. In channel deployments that used `toolsBySender` or group policy to deny `read` for less-trusted senders, a denied sender could still trigger host-media attachment loading and cause readable local files to be returned through the outbound media path.

## Affected Versions

This issue is known to affect OpenClaw 2026.4.9. Earlier versions were not confirmed during triage, so the advisory range is intentionally scoped to `>= 2026.4.9 < 2026.4.10`.

## Impact

Affected deployments are those that both allow host read or filesystem root expansion at the global/agent level and rely on sender or group-scoped policy to deny `read` for some channel participants. In that configuration, the intended sender/group authorization boundary could be bypassed for outbound media reads, potentially disclosing host-local files readable by the OpenClaw process.

The issue does not require treating the model prompt as the security boundary. The vulnerable behavior was a concrete policy enforcement mismatch: sender/group policy denied `read`, while the host-media read helper could still be installed without that sender context.

## Resolution

Fixed in OpenClaw 2026.4.10 by PR #64459, commit `c949af9fabf3873b5b7c484090cb5f5ab6049a98`. The fix threads sender, session, channel, and account context into outbound media access resolution and intersects host-media read capability creation with the existing group tool policy for `read`. When a concrete sender/group override denies `read`, OpenClaw no longer creates the host `readFile` media capability.

Additional attachment canonicalization hardening shipped in 2026.4.14, but the authorization bypass described here was fixed in 2026.4.10.

## Credit

Thanks to @Telecaster2147 for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jhpv-5j76-m56h
- https://github.com/openclaw/openclaw/pull/64459
- https://github.com/openclaw/openclaw/commit/c949af9fabf3873b5b7c484090cb5f5ab6049a98
- https://github.com/openclaw/openclaw
