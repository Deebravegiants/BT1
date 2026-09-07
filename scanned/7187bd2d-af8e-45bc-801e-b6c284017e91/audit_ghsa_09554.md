# [H] Jenkins Email Extension Plugin: Attackers able to control email content may specify `file:` URLs for images to read arbitrary files from Jenkins controller filesystem

## Summary
Severity: High
Advisory: GHSA-mq58-m26g-46gp
CVE: CVE-2026-48920
CWE: CWE-73
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-mq58-m26g-46gp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <1933.1935.v276319e3cc47

## Details
Jenkins Email Extension Plugin 1933.v45cec755423f and earlier includes a feature that allows inlining images as `base64` in email content by setting the `data-inline` attribute. No restrictions are placed on the image URLs that can be inlined.

This allows attackers able to control the email content to specify `file:` URLs for images to read arbitrary files from the Jenkins controller filesystem.

The feature allowing inlining images as `base64` in email content by setting the `data-inline` attribute is removed from Email Extension Plugin 1933.1935.v276319e3cc47.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48920
- https://github.com/jenkinsci/email-ext-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3705
