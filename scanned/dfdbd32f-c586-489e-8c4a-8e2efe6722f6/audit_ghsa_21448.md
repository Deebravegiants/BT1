# [M] XSS via uploaded gpx file

## Summary
Severity: Medium
Advisory: GHSA-vv3r-fxqp-vr3f
CVE: CVE-2022-38147
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-vv3r-fxqp-vr3f
Type: github-advisory

## Affected
- Packagist: `silverstripe/assets` — affected >=1.0.0 <1.11.1

## Details
A malicious content author could upload a GPX file with a Javascript payload. The payload could then be executed by luring a legitimate user to view the file in a browser with support for GPX files. GPX is an XML-based format used to store GPS data.

By default, Silverstripe CMS will no longer allow GPX files to be uploaded to the assets area.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38147
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/assets/CVE-2022-38147.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-38147
