# [M] Yamcs Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4cqv-q33x-wfxw
CVE: CVE-2023-45279
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-4cqv-q33x-wfxw
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs` — affected >=0 <5.8.7

## Details
Yamcs 5.8.6 allows XSS (issue 1 of 2). It comes with a Bucket as its primary storage mechanism. Buckets allow for the upload of any file. There's a way to upload a display referencing a malicious JavaScript file to the bucket. The user can then open the uploaded display by selecting Telemetry from the menu and navigating to the display.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45279
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/compare/yamcs-5.8.6...yamcs-5.8.7
- https://www.linkedin.com/pulse/yamcs-vulnerability-assessment-visionspace-technologies
