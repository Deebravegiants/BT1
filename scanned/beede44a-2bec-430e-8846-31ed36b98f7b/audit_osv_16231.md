# [M] CVE-2019-3794

## Summary
Severity: Medium
Advisory: CVE-2019-3794
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-3794
Type: osv

## Details
Cloud Foundry UAA, versions prior to v73.4.0, does not set an X-FRAME-OPTIONS header on various endpoints. A remote user can perform clickjacking attacks on UAA's frontend sites.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3794
