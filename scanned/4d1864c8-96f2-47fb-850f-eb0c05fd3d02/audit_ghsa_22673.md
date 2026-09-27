# [M] Insertion of Sensitive Information into Log File in Jenkins Configuration as Code Plugin

## Summary
Severity: Medium
Advisory: GHSA-7c3v-vc3x-x789
CVE: CVE-2019-10367
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7c3v-vc3x-x789
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <1.27

## Details
Configuration as Code Plugin logs the changes it applies to the Jenkins system log. Secrets such as passwords should be masked (i.e. replaced with asterisks) in that log to prevent accidental disclosure. Configuration as Code Plugin inspects the type and looks for a field, getter, or constructor argument corresponding to the property, making the secret detection much more robust for the purpose of log message masking. This was implemented in the [fix for SECURITY-1279 in the 2019-07-31 security advisory](https://www.jenkins.io/security/advisory/2019-07-31/#SECURITY-1279).

That fix was incomplete and did not cover a log message written to the logger `io.jenkins.plugins.casc.impl.configurators.DataBoundConfigurator`.

Configuration as Code Plugin now uses the same secret detection for these log messages.

As a workaround, administrators can configure the logging level of the logger `io.jenkins.plugins.casc.impl.configurators.DataBoundConfigurator` to a level that does not include these messages. Configuration as Code Plugin 1.25 and earlier logs these messages at the `INFO` level, Configuration as Code Plugin 1.26 logs them at `FINE`. See the logging documentation for details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10367
- https://github.com/jenkinsci/configuration-as-code-plugin/commit/322ef83f3200ce6076129c014209ef938e556774
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1497
- https://www.jenkins.io/security/advisory/2019-07-31/#SECURITY-1279
- http://www.openwall.com/lists/oss-security/2019/08/07/1
