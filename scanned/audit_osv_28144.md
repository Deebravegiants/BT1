# [M] XML external entity (XXE) injection in OpenOLAT

## Summary
Severity: Medium
Advisory: CVE-2024-28198
Aliases: GHSA-pqvm-h9mg-434c
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-11
Source: https://osv.dev/vulnerability/CVE-2024-28198
Type: osv

## Details
OpenOlat is an open source web-based e-learning platform for teaching, learning, assessment and communication. By manually manipulating http requests when using the draw.io integration it is possible to read arbitrary files as the configured system user and SSRF. The problem is fixed in version 18.1.6 and 18.2.2. It is advised to upgrade to the latest version of 18.1.x or 18.2.x. Users unable to upgrade may work around this issue by disabling the Draw.io module or the entire REST API which will secure the system.

## References
- https://track.frentix.com/issue/OO-7553/XXE-injection-in-draw.io-endpoint
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28198.json
- https://github.com/OpenOLAT/OpenOLAT/security/advisories/GHSA-pqvm-h9mg-434c
- https://nvd.nist.gov/vuln/detail/CVE-2024-28198
- https://github.com/OpenOLAT/OpenOLAT/commit/23e6212e9412c3b099436159b8c8935321c91872
