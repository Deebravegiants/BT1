# [M] Improper Restriction of XML External Entity Reference in skylot/jadx

## Summary
Severity: Medium
Advisory: GHSA-r8j4-96mx-rjcc
CVE: CVE-2022-0219
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-r8j4-96mx-rjcc
Type: github-advisory

## Affected
- Maven: `io.github.skylot:jadx-core` — affected >=0 <1.3.2

## Details
skylot/jadx prior to 1.3.2 is vulnerable to Improper Restriction of XML External Entities when a user is tricked into exporting a malicious APK file (via the -e option) containing a crafted AndroidManifest.xml / strings.xml to gradle, leading to possible local file disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0219
- https://github.com/skylot/jadx/commit/d22db30166e7cb369d72be41382bb63ac8b81c52
- https://github.com/skylot/jadx
- https://huntr.dev/bounties/0d093863-29e8-4dd7-a885-64f76d50bf5e
