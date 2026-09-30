# [M] Possible information disclosure of environment variables in Vaadin Build Plugins via Failed Frontend Build

## Summary
Severity: Medium
Advisory: CVE-2026-7860
Aliases: GHSA-j8mx-j73w-9mxw
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:P/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N/E:U/S:N/AU:N/R:A/V:C/RE:L/U:Green)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-7860
Type: osv

## Details
A possible information disclosure vulnerability exists in the Vaadin Maven plugin and Vaadin Gradle plugin that exposes the full set of environment variables in build logs whenever the frontend build process exits with a non-zero status. Because the build environment may contain credentials supplied as secrets, any failed frontend build can expose those secrets in clear text in CI logs and archived build artifacts.


Users of affected versions should apply the following mitigation or upgrade. Releases that have fixed this issue include:

Product version
Vaadin 23.0.0 - 23.6.9
Vaadin 24.0.0 - 24.9.16
Vaadin 24.10.0 - 24.10.3
Vaadin 25.0.0 - 25.0.10
Vaadin 25.1.0 - 25.1.4

Mitigation
Upgrade to 23.6.10
Upgrade to 24.9.17 or newer
Upgrade to 24.10.4 or newer
Upgrade to 25.0.11 or newer
Upgrade to 25.1.5 or newer

Please note that Vaadin versions 10-13 and 15-22 are no longer supported and you should update either to the latest 23, 24, or 25 version.

ArtifactsMaven coordinatesVulnerable versionsFixed versioncom.vaadin:flow-plugin-base23.0.0 - 23.6.10≥23.6.11com.vaadin:flow-plugin-base24.0.0 - 24.9.17≥24.9.18com.vaadin:flow-plugin-base24.10.0 - 24.10.3≥24.10.4com.vaadin:flow-plugin-base25.0.0 - 25.0.11≥25.0.12com.vaadin:flow-plugin-base25.1.0 - 25.1.4≥25.1.5com.vaadin:flow-maven-plugin23.0.0 - 23.6.10≥23.6.11com.vaadin:flow-maven-plugin24.0.0 - 24.9.17≥24.9.18com.vaadin:flow-maven-plugin24.10.0 - 24.10.3≥24.10.4com.vaadin:flow-maven-plugin25.0.0 - 25.0.11≥25.0.12com.vaadin:flow-maven-plugin25.1.0 - 25.1.4≥25.1.5com.vaadin:flow-gradle-plugin24.0.0 - 24.9.17≥24.9.18com.vaadin:flow-gradle-plugin24.10.0 - 24.10.3≥24.10.4com.vaadin:flow-gradle-plugin25.0.0 - 25.0.11≥25.0.12com.vaadin:flow-gradle-plugin25.1.0 - 25.1.4≥25.1.5

## References
- https://repo.maven.apache.org/maven2
- https://vaadin.com/security/cve-2026-7860
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7860.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7860
- https://github.com/vaadin/flow/pull/24219
- https://github.com/vaadin/flow
