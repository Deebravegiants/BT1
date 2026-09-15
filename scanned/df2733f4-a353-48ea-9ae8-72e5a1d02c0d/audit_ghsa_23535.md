# [H] Use of Insufficiently Random Values in Apereo CAS

## Summary
Severity: High
Advisory: GHSA-g24w-373r-5pxg
CVE: CVE-2019-10754
CWE: CWE-330, CWE-338
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g24w-373r-5pxg
Type: github-advisory

## Affected
- Maven: `org.apereo.cas:cas-server-support-simple-mfa` — affected >=0 <6.1.0-RC5
- Maven: `org.apereo.cas:cas-server-support-oidc` — affected >=0 <6.1.0-RC5
- Maven: `org.apereo.cas:cas-server-core-services-api` — affected >=0 <6.1.0-RC5
- Maven: `org.apereo.cas:cas-server-support-oauth-core-api` — affected >=0 <6.1.0-RC5
- Maven: `org.apereo.cas:cas-server-support-shell` — affected >=0 <6.1.0-RC5
- Maven: `org.apereo.cas:cas-server-core-services-authentication` — affected >=0 <6.1.0-RC5

## Details
Multiple classes used within Apereo CAS before release 6.1.0-RC5 makes use of apache commons-lang3 RandomStringUtils for token and ID generation which makes them predictable due to RandomStringUtils PRNG's algorithm not being cryptographically strong.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10754
- https://github.com/apereo/cas/commit/40bf278e66786544411c471de5123e7a71826b9f
- https://github.com/apereo/cas
- https://snyk.io/vuln/SNYK-JAVA-ORGAPEREOCAS-467402
- https://snyk.io/vuln/SNYK-JAVA-ORGAPEREOCAS-467404
- https://snyk.io/vuln/SNYK-JAVA-ORGAPEREOCAS-467406
- https://snyk.io/vuln/SNYK-JAVA-ORGAPEREOCAS-468868
- https://snyk.io/vuln/SNYK-JAVA-ORGAPEREOCAS-468869
