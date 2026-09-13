# [M] smol-toml: Denial of Service via malformed TOML documents

## Summary
Severity: Medium
Advisory: CVE-2026-85730
Aliases: GHSA-7w5x-hrqm-74c2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85730
Type: osv

## Details
smol-toml is a small, fast, and correct TOML parser and serializer. Prior to 1.7.1, parse() can enter an infinite loop when a value inside an array or inline table is followed by a comment with no trailing newline. In src/util.ts, skipUntil() calls indexOfNewline(), receives -1 at the end of input, and resets the cursor to the beginning of the string instead of leaving the structure scan. The parser then hangs indefinitely and can consume a service's processing capacity when an application parses attacker-controlled TOML. This issue is fixed in version 1.7.1.

## References
- https://github.com/squirrelchat/smol-toml/releases/tag/v1.7.1
- https://medium.com/@ravindu.lakmina1/seven-bytes-that-freeze-a-node-js-server-forever-the-story-of-cve-2026-85730-3213328b38f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85730.json
- https://github.com/squirrelchat/smol-toml/security/advisories/GHSA-7w5x-hrqm-74c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-85730
- https://github.com/squirrelchat/smol-toml/commit/30f5c367d946b695f379b5d4f0946b2f0a0a8c2f
