# [M] CVE-2021-22916

## Summary
Severity: Medium
Advisory: CVE-2021-22916
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-22916
Type: osv

## Details
In Brave Desktop between versions 1.17 and 1.26.60, when adblocking is enabled and a proxy browser extension is installed, the CNAME adblocking feature issues DNS requests that used the system DNS settings instead of the extension's proxy settings, resulting in possible information disclosure.

## References
- https://hackerone.com/reports/1203842
