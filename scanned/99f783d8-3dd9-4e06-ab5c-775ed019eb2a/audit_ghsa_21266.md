# [M] Apache Isis webconsole module may directly query the database in prototype mode

## Summary
Severity: Medium
Advisory: GHSA-998r-j9rx-qm8m
CVE: CVE-2022-42467
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-998r-j9rx-qm8m
Type: github-advisory

## Affected
- Maven: `org.apache.isis.core:isis-core` — affected >=0 <2.0.0-M8

## Details
When running in prototype mode, the h2 webconsole module (accessible from the Prototype menu) is automatically made available with the ability to directly query the database. It was felt that it is safer to require the developer to explicitly enable this capability. As of 2.0.0-M8, this can now be done using the `isis.prototyping.h2-console.web-allow-remote-access` configuration property; the web console will be unavailable without setting this configuration. As an additional safeguard, the new `isis.prototyping.h2-console.generate-random-web-admin-password` configuration parameter (enabled by default) requires that the administrator use a randomly generated password to use the console. The password is printed to the log, as `webAdminPass: xxx` (where `xxx`) is the password. To revert to the original behaviour, the administrator would therefore need to set these configuration parameter: `isis.prototyping.h2-console.web-allow-remote-access=true isis.prototyping.h2-console.generate-random-web-admin-password=false` Note also that the h2 webconsole is never available in production mode, so these safeguards are only to ensure that the webconsole is secured by default also in prototype mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42467
- https://github.com/apache/isis/commit/9fcab9816dac37e0f07ffe3f5c4f47df9cec8694
- https://github.com/apache/isis
- https://lists.apache.org/thread/jbv2ddt00h7ntlbm6vkk4wdmb31pm8q3
- http://www.openwall.com/lists/oss-security/2022/10/19/1
