# [C] Jenkins Pipeline: Groovy Plugin allows sandbox protection bypass and arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-mqc2-w9r8-mmxm
CVE: CVE-2022-43402
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-mqc2-w9r8-mmxm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps` — affected >=0 <2803.v1a_f77ffcc773

## Details
A sandbox bypass vulnerability involving various casts performed implicitly by the Groovy language runtime in Jenkins Pipeline: Groovy Plugin 2802.v5ea_628154b_c2 and earlier allows attackers with permission to define and run sandboxed scripts, including Pipelines, to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM. Pipeline: Groovy Plugin 2803.v1a_f77ffcc773 intercepts Groovy casts performed implicitly by the Groovy language runtime

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43402
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2824%20(1)
- http://www.openwall.com/lists/oss-security/2022/10/19/3
