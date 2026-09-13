# [M] mitmproxy binaries embed a vulnerable python-hyper/h2 dependency

## Summary
Severity: Medium
Advisory: GHSA-63cx-g855-hvv4
CWE: CWE-1395, CWE-444
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-08-25
Source: https://github.com/advisories/GHSA-63cx-g855-hvv4
Type: github-advisory

## Affected
- PyPI: `mitmproxy` — affected >=0 <12.1.2

## Details
mitmproxy 12.1.1 and below embed python-hyper/h2 ≤ v4.2.0, which has a gap in its HTTP/2 header validation. This enables request smuggling attacks when mitmproxy is in a configuration where it translates HTTP/2 to HTTP/1. For example, this affects reverse proxies to `http://` backends. It does not affect mitmproxy's regular mode.

All users are encouraged to upgrade to mitmproxy 12.1.2, which includes a fixed version of h2.

More details about the vulnerability itself can be found at https://github.com/python-hyper/h2/security/advisories/GHSA-847f-9342-265h.

## References
- https://github.com/mitmproxy/mitmproxy/security/advisories/GHSA-63cx-g855-hvv4
- https://github.com/python-hyper/h2/security/advisories/GHSA-847f-9342-265h
- https://github.com/mitmproxy/mitmproxy
