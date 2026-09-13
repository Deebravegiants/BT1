# [H] CVE-2021-22142

## Summary
Severity: High
Advisory: CVE-2021-22142
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/CVE-2021-22142
Type: osv

## Details
Kibana contains an embedded version of the Chromium browser that the Reporting feature uses to generate the downloadable reports. If a user with permissions to generate reports is able to render arbitrary HTML with this browser, they may be able to leverage known Chromium vulnerabilities to conduct further attacks. Kibana contains a number of protections to prevent this browser from rendering arbitrary content.

## References
- https://discuss.elastic.co/t/elastic-stack-7-13-0-and-6-8-16-security-update/273964/1
- https://www.elastic.co/community/security
