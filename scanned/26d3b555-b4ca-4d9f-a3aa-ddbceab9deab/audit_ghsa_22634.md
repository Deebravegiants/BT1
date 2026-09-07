# [C] Deserialization of Untrusted Data in NancyFX Nancy

## Summary
Severity: Critical
Advisory: GHSA-mx3q-j2g2-5qxq
CVE: CVE-2017-9785
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mx3q-j2g2-5qxq
Type: github-advisory

## Affected
- NuGet: `Nancy` — affected >=0 <1.4.4
- NuGet: `Nancy` — affected >=2.0.0-alpha <2.0.0

## Details
Csrf.cs in NancyFX Nancy before 1.4.4 and 2.x before 2.0-dangermouse has Remote Code Execution via Deserialization of JSON data in a CSRF Cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9785
- https://github.com/NancyFx/Nancy/releases/tag/v1.4.4
