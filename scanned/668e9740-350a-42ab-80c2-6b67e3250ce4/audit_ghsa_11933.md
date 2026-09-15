# [M] HybridAuth Has Improper SSL Certificate Validation in Curl HTTP Client

## Summary
Severity: Medium
Advisory: GHSA-r3hf-q3mf-7h6w
CVE: CVE-2026-4587
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-r3hf-q3mf-7h6w
Type: github-advisory

## Affected
- Packagist: `hybridauth/hybridauth` — affected >=0

## Details
A vulnerability was found in HybridAuth up to 3.12.2. This issue affects some unknown processing of the file src/HttpClient/Curl.php of the component SSL Handler. The manipulation of the argument curlOptions results in improper certificate validation. The attack can be launched remotely. This attack is characterized by high complexity. The exploitability is assessed as difficult. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4587
- https://github.com/hybridauth/hybridauth/issues/1444
- https://github.com/hybridauth/hybridauth
- https://vuldb.com/?ctiid.352423
- https://vuldb.com/?id.352423
- https://vuldb.com/?submit.775463
