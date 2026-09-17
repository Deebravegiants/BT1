# [M] Moderate severity vulnerability that affects org.apache.spark:spark-core_2.10 and org.apache.spark:spark-core_2.11

## Summary
Severity: Medium
Advisory: GHSA-r34r-f84j-5x4x
CVE: CVE-2017-7678
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-r34r-f84j-5x4x
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.11` — affected >=0 <2.2.0
- Maven: `org.apache.spark:spark-core_2.10` — affected >=0 <2.2.0

## Details
In Apache Spark before 2.2.0, it is possible for an attacker to take advantage of a user's trust in the server to trick them into visiting a link that points to a shared Spark cluster and submits data including MHTML to the Spark master, or history server. This data, which could contain a script, would then be reflected back to the user and could be evaluated and executed by MS Windows-based clients. It is not an attack on Spark itself, but on the user, who may then execute the script inadvertently when viewing elements of the Spark web UIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7678
- https://github.com/advisories/GHSA-r34r-f84j-5x4x
- http://apache-spark-developers-list.1001551.n3.nabble.com/CVE-2017-7678-Apache-Spark-XSS-web-UI-MHTML-vulnerability-td21947.html
- http://www.securityfocus.com/bid/99603
