# [C] Bash command injection in Apache Zeppelin

## Summary
Severity: Critical
Advisory: GHSA-4qw8-pgpr-p9mq
CVE: CVE-2019-10095
CWE: CWE-77, CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-4qw8-pgpr-p9mq
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin` — affected >=0 <0.10.0

## Details
bash command injection vulnerability in Apache Zeppelin allows an attacker to inject system commands into Spark interpreter settings. This issue affects Apache Zeppelin Apache Zeppelin version 0.9.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10095
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread.html/rd56389ba9cab30a6c976b9a4a6df0f85cbe8fba6a60a3cf6e3ba716b%40%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/rd56389ba9cab30a6c976b9a4a6df0f85cbe8fba6a60a3cf6e3ba716b@%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/rdf06e8423833b3daadc30c56a2ff47c48920864d5199476daa897208%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rdf06e8423833b3daadc30c56a2ff47c48920864d5199476daa897208%40%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/rdf06e8423833b3daadc30c56a2ff47c48920864d5199476daa897208@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rdf06e8423833b3daadc30c56a2ff47c48920864d5199476daa897208@%3Cusers.zeppelin.apache.org%3E
- https://security.gentoo.org/glsa/202311-04
- http://www.openwall.com/lists/oss-security/2021/09/02/1
