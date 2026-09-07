# [H] WildFly has incomplete blacklist vulnerability

## Summary
Severity: High
Advisory: GHSA-9q87-22gr-r8qf
CVE: CVE-2016-0793
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9q87-22gr-r8qf
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-parent` — affected >=0 <10.0.0.Final
- Maven: `org.wildfly:wildfly-undertow` — affected >=0 <10.0.0.Final

## Details
Incomplete blacklist vulnerability in the servlet filter restriction mechanism in WildFly (formerly JBoss Application Server) before 10.0.0.Final on Windows allows remote attackers to read the sensitive files in the (1) WEB-INF or (2) META-INF directory via a request that contains (a) lowercase or (b) "meaningless" characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0793
- https://bugzilla.redhat.com/show_bug.cgi?id=1305937
- https://github.com/wildfly/wildfly
- https://security.netapp.com/advisory/ntap-20180215-0001
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03784en_us
- https://www.exploit-db.com/exploits/39573
- http://packetstormsecurity.com/files/136323/Wildfly-Filter-Restriction-Bypass-Information-Disclosure.html
