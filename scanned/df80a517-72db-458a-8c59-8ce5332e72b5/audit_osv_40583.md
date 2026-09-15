# [C] Looking Glass: Remote Code Execution via Unanchored Regular Expression in BGPASPath Input Validation

## Summary
Severity: Critical
Advisory: CVE-2026-53611
Aliases: GHSA-8hgf-p844-425m
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-53611
Type: osv

## Details
Looking Glass is a modern, stateless network-diagnostic platform — a single self-contained Go binary that fronts a fleet of routers over SSH and exposes ping / traceroute / BGP lookups through a gRPC (ConnectRPC) API, an embedded SvelteKit web UI, and a lg-cli client. Prior to version 1.3.5, there is an OS Command Injection vulnerability resulting from an unanchored regular expression in the input validation layer. This issue has been patched in version 1.3.5.

## References
- https://github.com/AS203038/looking-glass/releases/tag/1.3.5
- https://github.com/AS203038/looking-glass/security/advisories/GHSA-8hgf-p844-425m
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53611
