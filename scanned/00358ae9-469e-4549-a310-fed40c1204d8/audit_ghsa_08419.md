# [H] Plug.Cowboy vulnerable to unauthenticated remote DoS via HTTP/2 `:scheme` atom-table exhaustion

## Summary
Severity: High
Advisory: GHSA-q8x4-x7mp-5vg2
CVE: CVE-2026-32688
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-q8x4-x7mp-5vg2
Type: github-advisory

## Affected
- Hex: `plug_cowboy` — affected >=2.0.0 <2.8.1

## Details
## Summary

An unauthenticated remote denial-of-service vulnerability in `Plug.Cowboy.Conn` allows any attacker who can reach an HTTPS Plug.Cowboy listener via HTTP/2 to permanently exhaust the BEAM atom table and crash the entire Erlang VM.

## Am I Affected?

All users running plug_cowboy with HTTP/2 may be affected, this includes Phoenix applications. If another HTTP adapter such as Bandit is used, then the consuming project is not affected. If the HTTP/2 endpoint is exposed directly (without a proxy) then the project will be affected. If a proxy is in use then it depends on the proxy configuration. Many proxies use HTTP/1.1 internally, and would be unaffected.

## Impact

The vulnerability will allow crashing the Erlang VM (BEAM) via atom exhaustion.

## Mitigation

Users are advised to update to plug_cowboy v2.8.1 to mitigate this issue.

## Credits
Plug.Cowboy thanks Peter Ullrich for finding and responsibly disclosing this vulnerability.

## References
- https://github.com/elixir-plug/plug_cowboy/security/advisories/GHSA-q8x4-x7mp-5vg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32688
- https://github.com/elixir-plug/plug_cowboy/commit/bfb34cb45eb354e56437f7023fb306de1bf9c19b
- https://cna.erlef.org/cves/CVE-2026-32688.html
- https://github.com/elixir-plug/plug_cowboy
- https://osv.dev/vulnerability/EEF-CVE-2026-32688
