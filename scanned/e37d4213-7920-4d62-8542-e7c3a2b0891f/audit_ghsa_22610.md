# [H] Sandbox bypass vulnerability through implicitly allowlisted platform Groovy files in Jenkins Pipeline: Groovy Plugin

## Summary
Severity: High
Advisory: GHSA-2xvx-rw9p-xgfc
CVE: CVE-2022-30945
CWE: CWE-434, CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-2xvx-rw9p-xgfc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps` — affected >=0 <2692.v76b

## Details
Pipeline: Groovy Plugin allows pipelines to load Groovy source files. This is intended to be used to allow Global Shared Libraries to execute without sandbox protection.

In Pipeline: Groovy Plugin 2689.v434009a_31b_f1 and earlier, any Groovy source files bundled with Jenkins core and plugins could be loaded this way and their methods executed. If a suitable Groovy source file is available on the classpath of Jenkins, sandbox protections can be bypassed.

The Jenkins security team has been unable to identify any Groovy source files in Jenkins core or plugins that would allow attackers to execute dangerous code. While the severity of this issue is declared as High due to the potential impact, successful exploitation is considered very unlikely.

Pipeline: Groovy Plugin 2692.v76b_089ccd026 restricts which Groovy source files can be loaded in Pipelines.

Groovy source files in public plugins intended to be executed in sandboxed pipelines have been identified and added to an allowlist. The new extension point `org.jenkinsci.plugins.workflow.cps.GroovySourceFileAllowlist` allows plugins to add specific Groovy source files to that allowlist if necessary, but creation of plugin-specific Pipeline DSLs is strongly discouraged.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30945
- https://github.com/jenkinsci/workflow-cps-plugin/commit/76a7681702f42d65f77bbaa5463f146876ea62db
- https://github.com/jenkinsci/workflow-cps-plugin/commit/76b089ccd026b68012b0deb30c217395f7ca7dc2
- https://github.com/jenkinsci/workflow-cps-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-359
- http://www.openwall.com/lists/oss-security/2022/05/17/8
