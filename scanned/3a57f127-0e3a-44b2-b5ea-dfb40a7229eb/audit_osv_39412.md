# [H] Roxy-WI: Path-traversal patch in commit d4d10006 is a no-op (tuple-membership bug)

## Summary
Severity: High
Advisory: CVE-2026-45569
Aliases: GHSA-j6p4-8532-h9hv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45569
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, ommit d4d10006 ("Expand validation to block .. in config_file_name and configver for improved security") added a line in app/modules/config/config.py:462. This is tuple-membership, not substring containment — '..' in (a, b, c) evaluates to True only if any of a, b, c is equal to the literal string '..'. For any realistic path-traversal payload (../../etc/passwd, ..\\..\\etc\\passwd, etc.) the check returns False and the patch silently lets the payload through. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45569.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-j6p4-8532-h9hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45569
- https://github.com/roxy-wi/roxy-wi/commit/d4d10006
