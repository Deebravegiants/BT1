# [H] TERASOLUNA Server Framework vulnerable to ClassLoader manipulation

## Summary
Severity: High
Advisory: GHSA-q5j9-f95w-f4pr
CVE: CVE-2022-43484
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-q5j9-f95w-f4pr
Type: github-advisory

## Affected
- Maven: `org.terasoluna.gfw:terasoluna-gfw-common` — affected >=0 <1.0.1.RELEASE

## Details
TERASOLUNA Global Framework 1.0.0 (Public review version) and TERASOLUNA Server Framework for Java (Rich) 2.0.0.2 to 2.0.5.1 are vulnerable to ClassLoader manipulation due to using the old version of Spring Framework which contains the vulnerability. The vulnerability is caused by an improper input validation issue in the binding mechanism of Spring MVC. By the application processing a specially crafted file, arbitrary code may be executed with the privileges of the application. 

When using TERASOLUNA Global Framework 1.0.0 (Public review version), update to TERASOLUNA Server Framework for Java 5.7.1.SP1 (using Spring Framework 5.3.18). This vulnerability alone can be addressed by updating to TERASOLUNA Global Framework 1.0.1 (using Spring Framework 3.2.10) or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43484
- https://github.com/spring-projects/spring-framework/issues/15724
- https://github.com/terasolunaorg/terasoluna-gfw
- https://jvn.jp/en/jp/JVN54728399/index.html
- https://osdn.net/projects/terasoluna/wiki/cve-2022-43484
- http://terasolunaorg.github.io/vulnerability/cve-2022-43484.html
