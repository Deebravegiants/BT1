# [H] CVE-2020-5420

## Summary
Severity: High
Advisory: CVE-2020-5420
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/CVE-2020-5420
Type: osv

## Details
Cloud Foundry Routing (Gorouter) versions prior to 0.206.0 allow a malicious developer with "cf push" access to cause denial-of-service to the CF cluster by pushing an app that returns specially crafted HTTP responses that crash the Gorouters.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5420
