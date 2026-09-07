# [H] Sandbox bypass vulnerability in Jenkins Pipeline: Deprecated Groovy Libraries Plugin

## Summary
Severity: High
Advisory: GHSA-7qw2-h9gj-hcvh
CVE: CVE-2022-43406
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-7qw2-h9gj-hcvh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=0 <588.v576c103a_ff86
- Maven: `io.jenkins.plugins:pipeline-groovy-lib` — affected >=0 <613.v9c41a_160233f

## Details
Pipeline: Groovy Libraries Plugin and older releases of the Pipeline: Deprecated Groovy Libraries Plugin (formerly Pipeline: Shared Groovy Libraries Plugin) define the l`ibrary` Pipeline step, which allows Pipeline authors to dynamically load Pipeline libraries. The return value of this step can be used to instantiate classes defined in the loaded library.

In Pipeline: Groovy Libraries Plugin 612.v84da_9c54906d and earlier and in Pipeline: Deprecated Groovy Libraries Plugin 583.vf3b_454e43966 and earlier, the `library` step can be used to invoke sandbox-generated synthetic constructors in crafted untrusted libraries and construct any subclassable type. This is similar to SECURITY-582 in the [2017-08-07 security advisory](https://www.jenkins.io/security/advisory/2017-08-07/#multiple-groovy-language-features-allowed-script-security-plugin-sandbox-bypass), but in a different plugin.

This vulnerability allows attackers with permission to define untrusted Pipeline libraries and to define and run sandboxed Pipelines, to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM.

Pipeline: Groovy Libraries Plugin 613.v9c41a_160233f rejects improper calls to sandbox-generated synthetic constructors when using the `library` step.

Pipeline: Deprecated Groovy Libraries Plugin 588.v576c103a_ff86 no longer contains the `library` step. It has been moved into the Pipeline: Groovy Libraries Plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43406
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2824%20(2)
- http://www.openwall.com/lists/oss-security/2022/10/19/3
