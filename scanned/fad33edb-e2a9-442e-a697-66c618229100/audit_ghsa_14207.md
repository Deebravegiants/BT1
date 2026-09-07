# [M] Jenkins Thycotic DevOps Secrets Vault Plugin does not properly mask credentials

## Summary
Severity: Medium
Advisory: GHSA-f244-f9fc-w6fq
CVE: CVE-2023-30515
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-f244-f9fc-w6fq
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:thycotic-devops-secrets-vault` — affected >=0

## Details
Multiple Jenkins plugins do not properly mask (i.e., replace with asterisks) credentials printed in the build log from Pipeline steps like sh and bat, when both of the following conditions are met:

- The credentials are printed in build steps executing on an agent (typically inside a node block).

- Push mode for durable task logging is enabled. This is a hidden option in Pipeline: Nodes and Processes that can be enabled through the Java system property org.jenkinsci.plugins.workflow.steps.durable_task.DurableTaskStep.USE_WATCHING. It is also automatically enabled by some plugins, e.g., OpenTelemetry and Pipeline Logging over CloudWatch.

The following plugins are affected by this vulnerability:

- Kubernetes 3909.v1f2c633e8590 and earlier (SECURITY-3079 / CVE-2023-30513)

- Azure Key Vault 187.va_cd5fecd198a_ and earlier (SECURITY-3051 / CVE-2023-30514)

- Thycotic DevOps Secrets Vault 1.0.0 (SECURITY-3078 / CVE-2023-30515)

The following plugins have been updated to properly mask credentials in the build log when push mode for durable task logging is enabled:

- Kubernetes 3910.ve59cec5e33ea_ (SECURITY-3079 / CVE-2023-30513)

- Azure Key Vault 188.vf46b_7fa_846a_1 (SECURITY-3051 / CVE-2023-30514)

As of publication of this advisory, there is no fix available for the following plugin:

- Thycotic DevOps Secrets Vault 1.0.0 (SECURITY-3078 / CVE-2023-30515)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30515
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-3075
- http://www.openwall.com/lists/oss-security/2023/04/13/3
