# [H] NI MeasurementLink Python Services Improper Access Restriction vulnerability

## Summary
Severity: High
Advisory: GHSA-3f48-9j7q-q2gv
CVE: CVE-2023-4570
CWE: CWE-420
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-05
Source: https://github.com/advisories/GHSA-3f48-9j7q-q2gv
Type: github-advisory

## Affected
- PyPI: `ni-measurementlink-service` — affected >=0 <1.1.1
- PyPI: `ni-measurementlink-service` — affected >=1.2.0.dev0 <1.2.0

## Details
### Impact
An improper access restriction in NI MeasurementLink Python services could allow an attacker on an adjacent network to reach services exposed on localhost.  These services were previously thought to be unreachable outside of the node.  This affects measurement plug-ins written in Python using version 1.1.0 of the `ni-measurementlink-service` Python package and all previous versions.

### Patches
Upgrade all Python measurement plug-ins to use `ni-measurementlink-service` version 1.1.1 or later.

### References
Visit [ni.com/info](http://www.ni.com/info) and enter the info code `cve-2023-4570` for more information.

## References
- https://github.com/ni/measurementlink-python/security/advisories/GHSA-3f48-9j7q-q2gv
- https://nvd.nist.gov/vuln/detail/CVE-2023-4570
- https://github.com/ni/measurementlink-python/commit/3e9d45147befc9a151fca5582c64fa77c7ba1980
- https://github.com/ni/measurementlink-python/commit/d2c73b1e0252081e1b89767aa916d73772d04dd9
- https://github.com/ni/measurementlink-python
- https://www.ni.com/en/support/documentation/supplemental/23/improper-restriction-in-ni-measurementlink-python-services.html
