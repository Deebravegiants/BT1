# [H] Roxy-WI: EscapedString validator skips its '..' block when stripping (root cause for several path-traversal/RCE vectors)

## Summary
Severity: High
Advisory: CVE-2026-45565
Aliases: GHSA-7qm8-cm8p-9rx3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45565
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, EscapedString (app/modules/roxywi/class_models.py:16-30) is the centralised Pydantic validator used on dozens of fields including SSH credential name, username, description, etc. Its if/elif/elif/else flow returns the metacharacter-stripped value without also enforcing the .. block. An attacker who appends a single ;, &, |, $, or backtick to a .. payload routes the value through the strip arm, where .. survives unblocked and the result is not shlex.quote()'d either. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45565.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-7qm8-cm8p-9rx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45565
