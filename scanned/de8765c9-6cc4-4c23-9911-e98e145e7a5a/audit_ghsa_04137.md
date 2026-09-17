# [C] Unauthenticated Remote Code Execution in Apache JMeter

## Summary
Severity: Critical
Advisory: GHSA-wg37-7mrv-cfwm
CVE: CVE-2019-0187
CWE: CWE-327, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-03-07
Source: https://github.com/advisories/GHSA-wg37-7mrv-cfwm
Type: github-advisory

## Affected
- Maven: `org.apache.jmeter:ApacheJMeter` — affected >=0 <5.1

## Details
Unauthenticated RCE is possible when JMeter is used in distributed mode (-r or -R command line options). Attacker can establish a RMI connection to a jmeter-server using RemoteJMeterEngine and proceed with an attack using untrusted data deserialization. This only affect tests running in Distributed mode. Note that versions before 4.0 are not able to encrypt traffic between the nodes, nor authenticate the participating nodes so upgrade to JMeter 5.1 is also advised.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0187
- https://github.com/advisories/GHSA-wg37-7mrv-cfwm
- http://mail-archives.apache.org/mod_mbox/jmeter-user/201903.mbox/%3CCAH9fUpaUQaFbgY1Zh4OvKSL4wdvGAmVt%2Bn4fegibDoAxK5XARw%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/107219
