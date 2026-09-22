# [C] Opendaylight will authenticate any username and password combination

## Summary
Severity: Critical
Advisory: GHSA-qm24-4869-99pj
CVE: CVE-2015-1778
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qm24-4869-99pj
Type: github-advisory

## Affected
- Maven: `org.opendaylight.odlparent:opendaylight-karaf-resources` — affected >=0 <0.2.3-Helium-SR3

## Details
The custom authentication realm used by karaf-tomcat's "opendaylight" realm in Opendaylight before Helium SR3 will authenticate any username and password combination.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1778
- https://web.archive.org/web/20150510044305/https://git.opendaylight.org/gerrit/#/c/16307
- https://web.archive.org/web/20150510044305/https://wiki.opendaylight.org/view/Security_Advisories#.5BImportant.5D_CVE-2015-1778_OpenDaylight:_authentication_bypass
- github.com/opendaylight/odlparent
- http://www.openwall.com/lists/oss-security/2015/03/20/3
