# [H] CVE-2021-45884

## Summary
Severity: High
Advisory: CVE-2021-45884
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-27
Source: https://osv.dev/vulnerability/CVE-2021-45884
Type: osv

## Details
In Brave Desktop 1.17 through 1.33 before 1.33.106, when CNAME-based adblocking and a proxying extension with a SOCKS fallback are enabled, additional DNS requests are issued outside of the proxying extension using the system's DNS settings, resulting in information disclosure. NOTE: this issue exists because of an incomplete fix for CVE-2021-21323 and CVE-2021-22916.

## References
- https://github.com/brave/brave-browser/issues/20079
- https://hackerone.com/reports/1377864
- https://github.com/brave/brave-core/pull/10742
- https://github.com/brave/brave-browser/issues/19070
