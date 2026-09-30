# [M] Incorrect Resource Transfer Between Spheres in eclipse-wtp

## Summary
Severity: Medium
Advisory: GHSA-gvxv-5fp2-358q
CVE: CVE-2019-10753
CWE: CWE-669
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-09-11
Source: https://github.com/advisories/GHSA-gvxv-5fp2-358q
Type: github-advisory

## Affected
- Maven: `com.diffplug.spotless:spotless-eclipse-wtp` — affected >=0 <3.9.6
- Maven: `com.diffplug.spotless:spotless-eclipse-cdt` — affected >=0 <9.4.4
- Maven: `com.diffplug.spotless:spotless-eclipse-groovy` — affected >=0 <3.0.1

## Details
In all versions prior to version 3.9.6 for eclipse-wtp, all versions prior to version 9.4.4 for eclipse-cdt, and all versions prior to version 3.0.1 for eclipse-groovy, Spotless was resolving dependencies over an insecure channel (http). If the build occurred over an insecure connection, a malicious user could have perform a Man-in-the-Middle attack during the build and alter the build artifacts that were produced. In case that any of these artifacts were compromised, any developers using these could be altered. **Note:** In order to validate that this artifact was not compromised, the maintainer would need to confirm that none of the artifacts published to the registry were not altered with. Until this happens, we can not guarantee that this artifact was not compromised even though the probability that this happened is low.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10753
- https://github.com/diffplug/spotless/issues/360
- https://github.com/diffplug/spotless
- https://snyk.io/vuln/SNYK-JAVA-COMDIFFPLUGSPOTLESS-460377
