# [H] Cloud Foundry UAA SessionID present in Audit Event Logs

## Summary
Severity: High
Advisory: GHSA-xg5v-696h-c3vr
CVE: CVE-2018-1192
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xg5v-696h-c3vr
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <4.5.5
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.6.0 <4.7.4
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.8.0 <4.8.3

## Details
In Cloud Foundry Foundation cf-release versions prior to v285; cf-deployment versions prior to v1.7; UAA 4.5.x versions prior to 4.5.5, 4.8.x versions prior to 4.8.3, and 4.7.x versions prior to 4.7.4; and UAA-release 45.7.x versions prior to 45.7, 52.7.x versions prior to 52.7, and 53.3.x versions prior to 53.3, the SessionID is logged in audit event logs. An attacker can use the SessionID to impersonate a logged-in user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1192
- https://github.com/cloudfoundry/uaa/commit/1f529fcb43fd200cab10587e889343ef1683c6e6
- https://github.com/cloudfoundry/uaa/commit/599391fe5d564c7e4860b8a6ec17cda872a822a3
- https://github.com/cloudfoundry/uaa/commit/a61bfabbad22f646ecf1f00016b448b26a60daf
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/blog/cve-2018-1192
