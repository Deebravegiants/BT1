# [C] Deserialization of untrusted data in synthcity

## Summary
Severity: Critical
Advisory: GHSA-4957-7vhp-7v59
CVE: CVE-2024-0937
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-26
Source: https://github.com/advisories/GHSA-4957-7vhp-7v59
Type: github-advisory

## Affected
- PyPI: `synthcity` — affected >=0

## Details
A vulnerability, which was classified as critical, has been found in van_der_Schaar LAB synthcity 0.2.9. Affected by this issue is the function load_from_file of the component PKL File Handler. The manipulation leads to deserialization. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. VDB-252182 is the identifier assigned to this vulnerability. NOTE: The vendor was contacted early and confirmed immediately the existence of the issue. A patch is planned to be released in February 2024.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0937
- https://github.com/bayuncao/vul-cve-6
- https://github.com/vanderschaarlab/synthcity
- https://github.com/vanderschaarlab/synthcity/blob/73cfd8ca784f70141fc7f2969221cd3b5737f7b1/src/synthcity/utils/serialization.py#L30
- https://vuldb.com/?ctiid.252182
- https://vuldb.com/?id.252182
