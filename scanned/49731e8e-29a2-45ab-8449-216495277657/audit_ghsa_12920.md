# [M] typo3-appointments vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-cf5r-3pvm-w64w
CVE: CVE-2019-25094
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-04
Source: https://github.com/advisories/GHSA-cf5r-3pvm-w64w
Type: github-advisory

## Affected
- Packagist: `innologi/typo3-appointments` — affected >=0 <2.0.6

## Details
A vulnerability, which was classified as problematic, was found in innologi appointments Extension up to 2.0.5. This affects an unknown part of the component Appointment Handler. The manipulation of the argument formfield leads to cross site scripting. It is possible to initiate the attack remotely. Upgrading to version 2.0.6 is able to address this issue. The name of the patch is 986d3cb34e5e086c6f04e061f600ffc5837abe7f. It is recommended to upgrade the affected component. The identifier VDB-217353 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25094
- https://github.com/innologi/typo3-appointments/commit/986d3cb34e5e086c6f04e061f600ffc5837abe7f
- https://github.com/innologi/typo3-appointments
- https://github.com/innologi/typo3-appointments/releases/tag/2.0.6
- https://vuldb.com/?ctiid.217353
- https://vuldb.com/?id.217353
