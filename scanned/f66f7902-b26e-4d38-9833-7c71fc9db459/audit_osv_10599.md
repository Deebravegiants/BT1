# [H] CVE-2017-17697

## Summary
Severity: High
Advisory: CVE-2017-17697
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-12-15
Source: https://osv.dev/vulnerability/CVE-2017-17697
Type: osv

## Details
The Ping() function in ui/api/target.go in Harbor through 1.3.0-rc4 has SSRF via the endpoint parameter to /api/targets/ping.

## References
- https://github.com/vmware/harbor/issues/3755
