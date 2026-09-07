# [H] Session Fixation in WildFly Elytron

## Summary
Severity: High
Advisory: GHSA-7fhr-2694-rg79
CVE: CVE-2020-10714
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-7fhr-2694-rg79
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=0 <1.11.4

## Details
A flaw was found in WildFly Elytron version 1.11.3.Final and before. When using WildFly Elytron FORM authentication with a session ID in the URL, an attacker could perform a session fixation attack. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10714
- https://bugzilla.redhat.com/show_bug.cgi?id=1825714
- https://github.com/wildfly-security/wildfly-elytron
- https://security.netapp.com/advisory/ntap-20201223-0002
