# [M] Bokeh server applications have Incomplete Origin Validation in WebSockets

## Summary
Severity: Medium
Advisory: GHSA-793v-589g-574v
CVE: CVE-2026-21883
CWE: CWE-1385
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-793v-589g-574v
Type: github-advisory

## Affected
- PyPI: `bokeh` — affected >=0 <3.8.2

## Details
This vulnerability allows for **Cross-Site WebSocket Hijacking (CSWSH)** of a deployed Bokeh server instance. 

### Scope

This vulnerability is only relevant to deployed Bokeh server instances. There is no impact on static HTML output, standalone embedded plots, or Jupyter notebook usage. 

This vulnerability does not prevent any requirements for up-front authentication on Bokeh servers that have authentication hooks in place, and cannot be used to make Bokeh servers deployed on private, internal networks accessible outside those networks. 

### Impact

If a Bokeh server is configured with an allowlist (e.g., `dashboard.corp`), an attacker can register a domain like `dashboard.corp.attacker.com` (or use a subdomain if applicable) and lure a victim to visit it. The malicious site can then initiate a WebSocket connection to the vulnerable Bokeh server. Since the Origin header (e.g., `http://dashboard.corp.attacker.com/`) matches the allowlist according to the flawed logic, the connection is accepted.

Once connected, the attacker can interact with the Bokeh server on behalf of the victim, potentially accessing sensitive data, or modifying visualizations.

### Patches
Patched in versions 3.8.2 and later.

### Workarounds

None

### Technical description

The `match_host` function in `src/bokeh/server/util.py` contains a flaw in how it compares hostnames against the allowlist patterns. The function uses Python's `zip()` function to iterate over the parts of the hostname and the pattern simultaneously. However, `zip()` stops iteration when the shortest iterable is exhausted.

Because the code only checks if the *pattern* is longer than the *host* (lines 232-233), but fails to check if the *host* is longer than the *pattern*, a host that **starts** with the pattern (but has additional segments) will successfully match.

For example, if the allowlist is configured to `['[example.com](http://example.com/)']`, the function will incorrectly validate `[example.com.bad.com](http://example.com.evil.com/)` as a match:
1. `host` parts: `['example', 'com', 'bad', 'com']`
2. `pattern` parts: `['example', 'com']`
3. `zip` compares `example==example` (OK) and `com==com` (OK).
4. Iteration stops, and the function returns `True`.

## References
- https://github.com/bokeh/bokeh/security/advisories/GHSA-793v-589g-574v
- https://nvd.nist.gov/vuln/detail/CVE-2026-21883
- https://github.com/bokeh/bokeh/commit/cedd113b0e271b439dce768671685cf5f861812e
- https://aydinnyunus.github.io/2026/01/24/bokeh-websocket-hijacking-cve-2026-21883
- https://github.com/bokeh/bokeh
