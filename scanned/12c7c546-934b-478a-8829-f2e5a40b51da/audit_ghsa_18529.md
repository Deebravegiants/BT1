# [M] junit-platform-reporting can leak Git credentials through its OpenTestReportGeneratingListener 

## Summary
Severity: Medium
Advisory: GHSA-m43g-m425-p68x
CVE: CVE-2025-53103
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-07-01
Source: https://github.com/advisories/GHSA-m43g-m425-p68x
Type: github-advisory

## Affected
- Maven: `org.junit.platform:junit-platform-reporting` — affected >=5.12.0 <5.13.2

## Details
### Summary

This vulnerability affects JUnit's support for writing Open Test Reporting XML files which is an opt-in feature of `junit-platform-reporting`.

If a repository is cloned using a GitHub token or other credentials in its URL, for example:

```bash
git clone https://${GH_APP}:${GH_TOKEN}@github.com/example/example.git
```

The credentials are captured by `OpenTestReportGeneratingListener` which produces (trimmed for brevity):

```xml
<infrastructure>
    <git:repository originUrl="https://username:token@github.com/example/example.git" />
</infrastructure>
```

### Details

https://github.com/junit-team/junit5/blob/6b7764dac92fd35cb348152d1b37f8726875a4e0/junit-platform-reporting/src/main/java/org/junit/platform/reporting/open/xml/OpenTestReportGeneratingListener.java#L183

I think this should be configurable in some way to exclude select git information or exclude it entirely.

### PoC

1. Clone a repo using a GitHub token as shown above.
2. Enable the listener `junit.platform.reporting.open.xml.enabled=true`
3. Observe report captures credentials

### Impact

Depending on the level of access of the token, it can be nothing, limited, or everything.

If these test reports are published or stored anywhere public, then there is the possibility that a rouge attacker can steal the token and perform elevated actions by impersonating the user or app.

### Resolution

JUnit 5.13.2 and later replace credentials in the URL with `***`. Moreover, including any Git metadata in the XML output is now an opt-in feature that can be enabled via the new `junit.platform.reporting.open.xml.git.enabled=true` configuration parameter but is not included by default.

## References
- https://github.com/junit-team/junit-framework/security/advisories/GHSA-m43g-m425-p68x
- https://nvd.nist.gov/vuln/detail/CVE-2025-53103
- https://github.com/junit-team/junit-framework/commit/d4fc834c8c1c0b3168cd030c13551d1d041f51bc
- https://github.com/junit-team/junit-framework
- https://github.com/junit-team/junit-framework/blob/6b7764dac92fd35cb348152d1b37f8726875a4e0/junit-platform-reporting/src/main/java/org/junit/platform/reporting/open/xml/OpenTestReportGeneratingListener.java#L183
