# [H] CVE-2020-5417

## Summary
Severity: High
Advisory: CVE-2020-5417
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-5417
Type: osv

## Details
Cloud Foundry CAPI (Cloud Controller), versions prior to 1.97.0, when used in a deployment where an app domain is also the system domain (which is true in the default CF Deployment manifest), were vulnerable to developers maliciously or accidentally claiming certain sensitive routes, potentially resulting in the developer's app handling some requests that were expected to go to certain system components.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5417
