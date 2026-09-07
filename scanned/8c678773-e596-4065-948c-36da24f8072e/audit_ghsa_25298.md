# [H] Home Assistant information disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-mh78-8f49-vjg3
CVE: CVE-2018-21019
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mh78-8f49-vjg3
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <0.67.0

## Details
Home Assistant before 0.67.0 was vulnerable to an information disclosure that allowed an unauthenticated attacker to read the application's error log via components/api.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21019
- https://github.com/home-assistant/core/pull/13836
- https://github.com/home-assistant/home-assistant/pull/13836
- https://github.com/home-assistant/core/commit/598f093bf0fecdefaa3d95d1ddae71317a05321e
- https://github.com/home-assistant/core
- https://github.com/home-assistant/core/releases/tag/0.67.0
- https://github.com/home-assistant/home-assistant/releases/tag/0.67.0
- https://github.com/pypa/advisory-database/tree/main/vulns/homeassistant/PYSEC-2019-221.yaml
