# [H] Keycloak CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-7fmw-85qm-h22p
CVE: CVE-2017-12159
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7fmw-85qm-h22p
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <3.4.0

## Details
It was found that the cookie used for CSRF prevention in Keycloak was not unique to each session. An attacker could use this flaw to gain access to an authenticated user session, leading to possible information disclosure or further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12159
- https://access.redhat.com/errata/RHSA-2017:2904
- https://access.redhat.com/errata/RHSA-2017:2905
- https://access.redhat.com/errata/RHSA-2017:2906
- https://bugzilla.redhat.com/show_bug.cgi?id=1484111
- https://web.archive.org/web/20210124113906/http://www.securityfocus.com/bid/101601
