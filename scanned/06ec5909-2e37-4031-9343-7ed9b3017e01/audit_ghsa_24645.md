# [H] Password change doesn't result in Karaf clearing cache

## Summary
Severity: High
Advisory: GHSA-4px2-gqhv-mrc7
CVE: CVE-2017-1000406
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4px2-gqhv-mrc7
Type: github-advisory

## Affected
- Maven: `org.opendaylight.integration:distribution-karaf` — affected >=0

## Details
OpenDaylight Karaf 0.6.1-Carbon fails to clear the cache after a password change, allowing the old password to be used until the Karaf cache is manually cleared (e.g. via restart).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000406
- https://git.opendaylight.org/gerrit
- https://git.opendaylight.org/gerrit/#/q/topic:AAA-151
- https://jira.opendaylight.org/browse/AAA-151
- http://seclists.org/oss-sec/2017/q4/320
