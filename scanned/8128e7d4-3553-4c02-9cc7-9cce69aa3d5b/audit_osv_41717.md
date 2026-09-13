# [C] Faktory: Insecure predictable /tmp/redis.conf enables local Redis config hijack (network exposure / root RCE primitive)

## Summary
Severity: Critical
Advisory: CVE-2026-63404
Aliases: GHSA-j2vx-rpwf-w77v
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-63404
Type: osv

## Details
Faktory is a language-agnostic background job server. In versions prior to 1.10.0, the embedded Redis bootstrapper is vulnerable to an insecure temporary file flaw that lets a local unprivileged user hijack the Redis configuration and escalate to root. It writes its startup configuration to a fixed, predictable, world-writable path, /tmp/redis.conf, only creating the file if it does not already exist and never validating it on later boots. Because /tmp is world-writable, a local unprivileged user can pre-create /tmp/redis.conf with attacker-chosen Redis directives before Faktory starts, and Faktory will use the planted file verbatim. Faktory only overrides the unixsocket, dir, and logfile options, leaving directives such as bind, protected-mode, requirepass, and loadmodule attacker-controlled. This lets an attacker silently expose the entire job queue over an unauthenticated network port with no visible error to the administrator. Because the official systemd unit runs Faktory, and the redis-server child it spawns, as root, an attacker can also supply a loadmodule directive to execute arbitrary native code in the root-owned Redis process, escalating from a local unprivileged user to root. This issue is fixed in version 1.10.0.

## References
- https://github.com/contribsys/faktory/releases/tag/v1.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63404.json
- https://github.com/contribsys/faktory/security/advisories/GHSA-j2vx-rpwf-w77v
- https://nvd.nist.gov/vuln/detail/CVE-2026-63404
- https://github.com/contribsys/faktory/commit/0fb44c0a2b3c554857b53563ad0cf61295cd0c41
