# [C] Incomplete fix for Apache Log4j vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7rjr-3q55-vv33
CVE: CVE-2021-45046
CWE: CWE-502, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-7rjr-3q55-vv33
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.13.0 <2.16.0
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=0 <2.12.2
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.8.0 <1.9.2
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.10.0 <1.10.8
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.11.0 <1.11.11
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=2.0.0 <2.0.12

## Details
# Impact

The fix to address [CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228) in Apache Log4j 2.15.0 was incomplete in certain non-default configurations. This could allow attackers with control over Thread Context Map (MDC) input data when the logging configuration uses a non-default Pattern Layout with either a Context Lookup (for example, $${ctx:loginId}) or a Thread Context Map pattern (%X, %mdc, or %MDC) to craft malicious input data using a JNDI Lookup pattern resulting in a remote code execution (RCE) attack. 

## Affected packages
Only the `org.apache.logging.log4j:log4j-core` package is directly affected by this vulnerability. The `org.apache.logging.log4j:log4j-api` should be kept at the same version as the `org.apache.logging.log4j:log4j-core` package to ensure compatability if in use.

# Mitigation

Log4j 2.16.0 fixes this issue by removing support for message lookup patterns and disabling JNDI functionality by default. This issue can be mitigated in prior releases (< 2.16.0) by removing the JndiLookup class from the classpath (example: zip -q -d log4j-core-*.jar org/apache/logging/log4j/core/lookup/JndiLookup.class).

Log4j 2.15.0 restricts JNDI LDAP lookups to localhost by default. Note that previous mitigations involving configuration such as to set the system property `log4j2.formatMsgNoLookups` to `true` do NOT mitigate this specific vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45046
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/alert-cve-2021-44228.html
- https://www.openwall.com/lists/oss-security/2021/12/14/4
- https://www.kb.cert.org/vuls/id/930724
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00646.html
- https://www.debian.org/security/2021/dsa-5022
- https://www.cve.org/CVERecord?id=CVE-2021-44228
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-45046
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-log4j-qRuKNEbd
- https://security.gentoo.org/glsa/202310-16
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-log4j-qRuKNEbd
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2021-0032
- https://logging.apache.org/log4j/2.x/security.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SIG7FZULMNK2XF6FZRU4VWYDQXNMUGAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EOKPQGV24RRBBI4TBZUDQMM4MEH7MXCY
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SIG7FZULMNK2XF6FZRU4VWYDQXNMUGAJ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EOKPQGV24RRBBI4TBZUDQMM4MEH7MXCY
