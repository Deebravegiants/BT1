# [H] destiny.gg chat vulnerable to cross-site request forgery

## Summary
Severity: High
Advisory: GHSA-cjcc-46j8-xmr8
CVE: CVE-2020-36625
CWE: CWE-352, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-cjcc-46j8-xmr8
Type: github-advisory

## Affected
- Go: `github.com/destinygg/chat` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** A vulnerability was found in destiny.gg chat. It has been rated as problematic. This issue affects the function websocket.Upgrader of the file main.go. The manipulation leads to cross-site request forgery. The attack may be initiated remotely. The name of the patch is bebd256fc3063111fb4503ca25e005ebf6e73780. It is recommended to apply a patch to fix this issue. The identifier VDB-216521 was assigned to this vulnerability. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36625
- https://github.com/destinygg/chat/pull/35
- https://github.com/destinygg/chat/commit/bebd256fc3063111fb4503ca25e005ebf6e73780
- https://github.com/destinygg/chat
- https://vuldb.com/?id.216521
