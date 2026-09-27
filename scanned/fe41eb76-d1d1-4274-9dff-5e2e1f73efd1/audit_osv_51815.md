# [H] CVE-2021-4104

## Summary
Severity: High
Advisory: CVE-2021-4104
Aliases: GHSA-fp5r-v3w9-4333
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-14
Source: https://osv.dev/vulnerability/CVE-2021-4104
Type: osv

## Details
JMSAppender in Log4j 1.2 is vulnerable to deserialization of untrusted data when the attacker has write access to the Log4j configuration. The attacker can provide TopicBindingName and TopicConnectionFactoryBindingName configurations causing JMSAppender to perform JNDI requests that result in remote code execution in a similar fashion to CVE-2021-44228. Note this issue only affects Log4j 1.2 when specifically configured to use JMSAppender, which is not the default. Apache Log4j 1.2 reached end of life in August 2015. Users should upgrade to Log4j 2 as it addresses numerous other issues from the previous versions.

## References
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2022/01/18/3
- https://www.cve.org/CVERecord?id=CVE-2021-44228
- https://www.kb.cert.org/vuls/id/930724
- https://access.redhat.com/security/cve/CVE-2021-4104
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2021-0033
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://security.gentoo.org/glsa/202209-02
- https://security.gentoo.org/glsa/202310-16
- https://security.gentoo.org/glsa/202312-02
- https://security.gentoo.org/glsa/202312-04
- https://security.netapp.com/advisory/ntap-20211223-0007/
- https://github.com/apache/logging-log4j2/pull/608#issuecomment-990494126
