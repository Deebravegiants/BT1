# [H] Improper Restriction of XML External Entity Reference in DiffPlug Spotless

## Summary
Severity: High
Advisory: GHSA-7v35-qwwj-p98g
CVE: CVE-2019-9843
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-7v35-qwwj-p98g
Type: github-advisory

## Affected
- Maven: `com.diffplug.spotless:spotless-plugin-gradle` — affected >=0 <3.20.0
- Maven: `com.diffplug.spotless:spotless-maven-plugin` — affected >=0 <1.20.0

## Details
In DiffPlug Spotless before 1.20.0 (library and Maven plugin) and before 3.20.0 (Gradle plugin), the XML parser would resolve external entities over both HTTP and HTTPS and didn't respect the resolveExternalEntities setting. For example, this allows disclosure of file contents to a MITM attacker if a victim performs a spotlessApply operation on an untrusted XML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9843
- https://github.com/diffplug/spotless/issues/358
- https://github.com/diffplug/spotless/pull/369
- https://github.com/diffplug/spotless
- https://github.com/diffplug/spotless/blob/master/plugin-gradle/CHANGES.md#version-3200---march-11th-2018-javadoc-jcenter
- https://github.com/diffplug/spotless/blob/master/plugin-maven/CHANGES.md#version-1200---march-14th-2018-javadoc-jcenter
