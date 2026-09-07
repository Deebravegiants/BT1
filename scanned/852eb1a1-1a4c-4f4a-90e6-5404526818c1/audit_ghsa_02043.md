# [H] Cross-Site Scripting

## Summary
Severity: High
Advisory: GHSA-5h26-c766-g93v
CVE: CVE-2021-20293
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-15
Source: https://github.com/advisories/GHSA-5h26-c766-g93v
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-bom` — affected >=0
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=0

## Details
A reflected Cross-Site Scripting (XSS) flaw was found in RESTEasy in all versions of RESTEasy up to 4.6.0.Final, where it did not properly handle URL encoding when calling @javax.ws.rs.PathParam without any @Produces MediaType. This flaw allows an attacker to launch a reflected XSS attack. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20293
- https://bugzilla.redhat.com/show_bug.cgi?id=1942819
- https://security.netapp.com/advisory/ntap-20210727-0005
