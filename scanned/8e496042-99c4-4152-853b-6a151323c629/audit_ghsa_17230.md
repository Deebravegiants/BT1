# [M] Home Assistant Core before is vulnerable to Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-pp3g-xmm4-5cw9
CVE: CVE-2025-65713
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-23
Source: https://github.com/advisories/GHSA-pp3g-xmm4-5cw9
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <2025.8.0

## Details
Home Assistant Core before v2025.8.0 is vulnerable to Directory Traversal. The Downloader integration does not fully validate file paths during concatenation, leaving a path traversal vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65713
- https://github.com/home-assistant/core/pull/150046
- https://gist.github.com/GenoWang/7359360285e0fe21a7a58d10ff71d032
- https://github.com/home-assistant/core
- https://github.com/home-assistant/core/blob/a4d12694dae82f10e2ca9c524e44a22ab7dacf66/homeassistant/components/downloader/services.py#L32
- https://github.com/home-assistant/core/blob/a4d12694dae82f10e2ca9c524e44a22ab7dacf66/homeassistant/util/__init__.py#L20
- https://github.com/home-assistant/core/blob/a4d12694dae82f10e2ca9c524e44a22ab7dacf66/homeassistant/util/__init__.py#L32-L38
