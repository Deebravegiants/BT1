# [M] JetPack Exposure of Resource to Wrong Sphere

## Summary
Severity: Medium
Advisory: GHSA-5hr6-r8h6-wh22
CVE: CVE-2021-24374
CWE: CWE-284, CWE-639, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5hr6-r8h6-wh22
Type: github-advisory

## Affected
- Packagist: `automattic/jetpack` — affected >=0 <9.8

## Details
The Jetpack Carousel module of the JetPack WordPress plugin before 9.8 allows users to create a "carousel" type image gallery and allows users to comment on the images. A security vulnerability was found within the Jetpack Carousel module by nguyenhg_vcs that allowed the comments of non-published page/posts to be leaked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-24374
- https://github.com/Automattic/jetpack-production
- https://jetpack.com/2021/06/01/jetpack-9-8-engage-your-audience-with-wordpress-stories
- https://wpscan.com/vulnerability/08a8a51c-49d3-4bce-b7e0-e365af1d8f33
