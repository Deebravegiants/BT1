# [M] Command Injection in @theia/messages

## Summary
Severity: Medium
Advisory: GHSA-c94v-8fff-73ph
CVE: CVE-2021-28162
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-c94v-8fff-73ph
Type: github-advisory

## Affected
- npm: `@theia/messages` — affected >=0 <1.0.0

## Details
In Eclipse Theia versions up to and including 0.16.0, in the notification messages there is no HTML escaping, so Javascript code can run.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28162
- https://github.com/eclipse-theia/theia/issues/7283
- https://github.com/eclipse-theia/theia/pull/7289
- https://github.com/eclipse-theia/theia/blob/master/CHANGELOG.md#v100---26032020
