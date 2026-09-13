# [C] alchemist.vim vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-6x65-vqp7-5r63
CVE: CVE-2017-1000212
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6x65-vqp7-5r63
Type: github-advisory

## Affected
- Hex: `alchemist.vim` — affected >=0 <1.3.2

## Details
Elixir's vim plugin, alchemist.vim is vulnerable to remote code execution in the bundled alchemist-server. A malicious website can execute requests against an ephemeral port on localhost that are then evaluated as elixir code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000212
- https://github.com/tonini/alchemist-server/issues/14
- https://github.com/tonini/alchemist-server/pull/16
- https://elixirforum.com/t/static-and-session-security-fixes-for-plug/3913
- https://github.com/tonini/alchemist-server
