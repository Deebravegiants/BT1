# [M] OrchardCore vulnerable to HTML injection

## Summary
Severity: Medium
Advisory: GHSA-5gg9-gwj4-mqmj
CVE: CVE-2022-32173
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-04
Source: https://github.com/advisories/GHSA-5gg9-gwj4-mqmj
Type: github-advisory

## Affected
- NuGet: `OrchardCore` — affected >=1.0.0-rc1-11259 <1.4.0

## Details
OrchardCore versions starting with 1.0.0-rc1-11259 and prior to 1.4.0 are vulnerable to HTML injection. The vulnerability allows an authenticated user with an editor security role to inject a persistent HTML modal dialog component into the dashboard that will affect admin users. Version 1.4.0 contains a patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32173
- https://github.com/OrchardCMS/OrchardCore/pull/11729
- https://github.com/OrchardCMS/OrchardCore/commit/0163c88ddeaca39815d7e6e5ea1c8391085cc136
- https://github.com/OrchardCMS/OrchardCore
- https://www.mend.io/vulnerability-database/CVE-2022-32173
