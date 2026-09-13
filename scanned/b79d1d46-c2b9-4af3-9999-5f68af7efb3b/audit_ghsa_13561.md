# [M] Fides Information Disclosure Vulnerability in Config API Endpoint

## Summary
Severity: Medium
Advisory: GHSA-rjxg-rpg3-9r89
CVE: CVE-2023-46125
CWE: CWE-200, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-rjxg-rpg3-9r89
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=0 <2.22.1

## Details
### Impact
The Fides webserver API allows users to retrieve its configuration using the `GET api/v1/config` endpoint. The configuration data is filtered to suppress most sensitive configuration information before it is returned to the user, but even the filtered data contains information about the internals and the backend infrastructure, such as various settings, servers’ addresses and ports and database username. This information is useful for administrative users as well as attackers, thus it should not be revealed to low-privileged users.

This vulnerability allows Admin UI users with roles lower than the owner role e.g. the viewer role to retrieve the config information using the API. 

### Patches
The vulnerability has been patched in Fides version `2.22.1`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds
There are no workarounds.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-rjxg-rpg3-9r89
- https://nvd.nist.gov/vuln/detail/CVE-2023-46125
- https://github.com/ethyca/fides/commit/c9f3a620a4b4c1916e0941cb5624dcd636f06d06
- https://github.com/ethyca/fides
- https://github.com/ethyca/fides/releases/tag/2.22.1
