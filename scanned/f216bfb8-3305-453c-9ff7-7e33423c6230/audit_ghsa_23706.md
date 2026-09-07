# [M] Keycloak Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-v38p-mqq3-m6v5
CVE: CVE-2017-12158
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v38p-mqq3-m6v5
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <3.4.0

## Details
It was found that Keycloak would accept a HOST header URL in the admin console and use it to determine web resource locations. An attacker could use this flaw against an authenticated user to attain reflected XSS via a malicious server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12158
- https://access.redhat.com/errata/RHSA-2017:2904
- https://access.redhat.com/errata/RHSA-2017:2905
- https://access.redhat.com/errata/RHSA-2017:2906
- https://bugzilla.redhat.com/show_bug.cgi?id=1489161
- https://web.archive.org/web/20210124114020/http://www.securityfocus.com/bid/101618
