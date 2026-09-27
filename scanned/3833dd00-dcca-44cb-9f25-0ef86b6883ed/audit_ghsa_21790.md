# [M] Injection in DeltaSpike

## Summary
Severity: Medium
Advisory: GHSA-rhg5-fqr3-hrf5
CVE: CVE-2019-12416
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-rhg5-fqr3-hrf5
Type: github-advisory

## Affected
- Maven: `org.apache.deltaspike:deltaspike` — affected >=0 <1.9.4

## Details
we got reports for 2 injection attacks against the DeltaSpike windowhandler.js. This is only active if a developer selected the ClientSideWindowStrategy which is not the default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12416
- https://lists.apache.org/thread.html/r848d7d4c0bf637da55f01103eb8ba0fce344c295fda53264cbaa1568@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/r8f327712b2b07f867fde1e77cbafcf8cc6a3facaa693ffdd2c3285e3%40%3Cdev.deltaspike.apache.org%3E
