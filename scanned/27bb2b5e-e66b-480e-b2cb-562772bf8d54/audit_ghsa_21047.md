# [H] Togglz console missing cross-site request forgery (CSRF) protection

## Summary
Severity: High
Advisory: GHSA-697v-pxg3-j262
CVE: CVE-2020-28191
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-697v-pxg3-j262
Type: github-advisory

## Affected
- Maven: `org.togglz:togglz-console` — affected >=0 <2.9.4

## Details
Togglz is an implementation of the Feature Toggles pattern for Java. There is no CSRF protection in the togglz console and could allow an attacker to guess the CSRF token value. Version 2.9.4 adds the necessary CSRF protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28191
- https://github.com/togglz/togglz/pull/495
- https://github.com/togglz/togglz/commit/ed66e3f584de954297ebaf98ea4a235286784707
- https://github.com/togglz/togglz
- https://www.mend.io/vulnerability-database/CVE-2020-28191
