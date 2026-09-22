# [M] pretix: API leaks check-in data between events of the same organizer

## Summary
Severity: Medium
Advisory: GHSA-wr8q-c73g-m7gp
CVE: CVE-2026-5600
CWE: CWE-653
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-wr8q-c73g-m7gp
Type: github-advisory

## Affected
- PyPI: `pretix` — affected >=2026.3.0 <2026.3.1
- PyPI: `pretix` — affected >=2026.2.0 <2026.2.1
- PyPI: `pretix` — affected >=2025.10.0 <2026.1.2

## Details
A new API endpoint introduced in pretix 2025 that is supposed to return all check-in events of a specific event in fact returns all check-in events belonging to the respective organizer. This allows an API consumer to access information for all other events under the same organizer, even those they should not have access to.

These records contain information on the time and result of every ticket scan as well as the ID of the matched ticket. Example:

{
  "id": 123,
  "successful": true,
  "error_reason": null,
  "error_explanation": null,
  "position": 321,
  "datetime": "2020-08-23T09:00:00+02:00",
  "list": 456,
  "created": "2020-08-23T09:00:00+02:00",
  "auto_checked_in": false,
  "gate": null,
  "device": 1,
  "device_id": 1,
  "type": "entry"
}

An unauthorized user usually has no way to match these IDs (position) back to individual people.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5600
- https://github.com/pretix/pretix
- https://github.com/pypa/advisory-database/tree/main/vulns/pretix/PYSEC-2026-111.yaml
- https://pretix.eu/about/en/blog/20260408-release-2026-3-1
