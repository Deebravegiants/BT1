# [M] Wildfly has a memory leak vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qx3p-9mmp-4v8h
CVE: CVE-2020-27822
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qx3p-9mmp-4v8h
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-parent` — affected >=19.0.0.Final <21.0.2.Final
- Maven: `org.wildfly:wildfly-parent` — affected >=22.0.0.Alpha1 <22.0.0.Beta1

## Details
A flaw was found in Wildfly affecting versions 19.0.0.Final, 19.1.0.Final, 20.0.0.Final, 20.0.1.Final, and 21.0.0.Final. When an application uses the OpenTracing API's java-interceptors, there is a possibility of a memory leak. This flaw allows an attacker to impact the availability of the server. The highest threat from this vulnerability is to system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27822
- https://github.com/wildfly/wildfly/pull/13749
- https://github.com/wildfly/wildfly/pull/13779
- https://github.com/wildfly/wildfly/commit/67ef84fd7aab789a535b137e5e506fd29d212455
- https://github.com/wildfly/wildfly/commit/c8b02f6a0605f4e2abfeaf21d28b7fe76171004b
- https://bugzilla.redhat.com/show_bug.cgi?id=1904060
- https://github.com/wildfly/wildfly
- https://issues.redhat.com/browse/WFLY-14094
