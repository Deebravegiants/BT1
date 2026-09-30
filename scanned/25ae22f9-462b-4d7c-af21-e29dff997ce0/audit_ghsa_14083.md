# [M] Jenkins HashiCorp Vault Plugin has improper masking of credentials

## Summary
Severity: Medium
Advisory: GHSA-v3fv-v9m6-26g3
CVE: CVE-2023-33001
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-v3fv-v9m6-26g3
Type: github-advisory

## Affected
- Maven: `com.datapipe.jenkins.plugins:hashicorp-vault-plugin` — affected >=0

## Details
Jenkins HashiCorp Vault Plugin 360.v0a_1c04cf807d and earlier does not properly mask (i.e., replace with asterisks) credentials printed in the build log from Pipeline steps like `sh` and `bat`, when both of the following conditions are met:

- The credentials are printed in build steps executing on an agent (typically inside a `node` block).

- Push mode for durable task logging is enabled. This is a hidden option in Pipeline: Nodes and Processes that can be enabled through the Java system property `org.jenkinsci.plugins.workflow.steps.durable_task.DurableTaskStep.USE_WATCHING`. It is also automatically enabled by some plugins, e.g., OpenTelemetry and Pipeline Logging over CloudWatch.

An improvement in Credentials Binding 523.525.vb_72269281873 implements a workaround that applies build log masking even in affected plugins. This workaround is temporary and potentially incomplete, so it is still recommended that affected plugins be updated to resolve this issue.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33001
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3077
