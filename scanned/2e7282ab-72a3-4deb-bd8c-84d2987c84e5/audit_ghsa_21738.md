# [M] Improper Handling of Exceptional Conditions inn metadata-extractor

## Summary
Severity: Medium
Advisory: GHSA-p5pg-wm9q-8v6r
CVE: CVE-2022-24613
CWE: CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-p5pg-wm9q-8v6r
Type: github-advisory

## Affected
- Maven: `com.drewnoakes:metadata-extractor` — affected >=0 <2.18.0

## Details
metadata-extractor up to 2.16.0 can throw various uncaught exceptions while parsing a specially crafted JPEG file, which could result in an application crash. This could be used to mount a denial of service attack against services that use metadata-extractor library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24613
- https://github.com/drewnoakes/metadata-extractor/issues/561
- https://github.com/drewnoakes/metadata-extractor
