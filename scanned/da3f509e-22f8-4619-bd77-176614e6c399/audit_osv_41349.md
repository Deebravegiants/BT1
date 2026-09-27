# [H] Rancher Audit-Log Middleware Unauthenticated Memory Exhaustion Denial of Service

## Summary
Severity: High
Advisory: CVE-2026-59675
Aliases: GHSA-g4f6-44g4-23xm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-59675
Type: osv

## Details
When API audit logging is enabled, the middleware reads the entire HTTP request body into memory without enforcing a size limit on login endpoints. Because the audit middleware is positioned earlier in the handler chain than Rancher's APIBodyLimitingHandler, the body-size cap (default 1 MiB) is bypassed for requests that pass through the audit copyReqBody path. An unauthenticated attacker can send arbitrarily large request bodies to the public login endpoints, causing the Rancher Manager server process to allocate memory proportional to the supplied body size. With just a few concurrent connections, this can exhaust available memory and terminate the Rancher Manager plane process, making the Rancher API and UI unavailable and interrupting management of all downstream clusters.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59675.json
- https://github.com/rancher/rancher/security/advisories/GHSA-g4f6-44g4-23xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-59675
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-59675
