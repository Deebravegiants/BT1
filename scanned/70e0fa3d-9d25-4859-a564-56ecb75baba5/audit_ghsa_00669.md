# [H] Disabled Hostname Verification in Opencast

## Summary
Severity: High
Advisory: GHSA-44cw-p2hm-gpf6
CVE: CVE-2020-26234
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-12-08
Source: https://github.com/advisories/GHSA-44cw-p2hm-gpf6
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-kernel` — affected >=0 <7.9
- Maven: `org.opencastproject:opencast-kernel` — affected >=8.0 <8.9

## Details
Opencast before version 8.9 and 7.9 disables HTTPS hostname verification of its HTTP client used for a large portion of Opencast's HTTP requests.

Hostname verification is an important part when using HTTPS to ensure that the presented certificate is valid for the host. Disabling it can allow for man-in-the-middle attacks.

### Patches

This problem is fixed in Opencast 7.9 and Opencast 8.9

### Self-Signed Certificates

Please be aware that fixing the problem means that Opencast will not simply accept any self-signed certificates any longer without properly importing them. If you need those, please make sure to import them into the Java key store. Better yet, get a valid certificate e.g. from [Let's Encrypt](https://letsencrypt.org).

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-44cw-p2hm-gpf6
- https://nvd.nist.gov/vuln/detail/CVE-2020-26234
- https://github.com/opencast/opencast/commit/4225bf90af74557deaf8fb6b80b0705c9621acfc
