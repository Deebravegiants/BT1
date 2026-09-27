# [H] Wildfly-OpenSSL memory leak flaw

## Summary
Severity: High
Advisory: GHSA-hxj4-885f-grgp
CVE: CVE-2020-25644
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hxj4-885f-grgp
Type: github-advisory

## Affected
- Maven: `org.wildfly.openssl:wildfly-openssl-natives-parent` — affected >=0 <1.1.3.Final

## Details
A memory leak flaw was found in WildFly OpenSSL in versions prior to 1.1.3.Final, where it removes an HTTP session. It may allow the attacker to cause OOM leading to a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25644
- https://github.com/wildfly-security/wildfly-openssl-natives/pull/4
- https://github.com/wildfly-security/wildfly-openssl-natives/pull/4/files
- https://github.com/wildfly-security/wildfly-openssl-natives/commit/7c26514676f3fb0dee0bcaa7d4680f982372950f
- https://bugzilla.redhat.com/show_bug.cgi?id=1885485
- https://github.com/wildfly-security/wildfly-openssl-natives
- https://issues.redhat.com/browse/WFSSL-51
- https://security.netapp.com/advisory/ntap-20201016-0004
