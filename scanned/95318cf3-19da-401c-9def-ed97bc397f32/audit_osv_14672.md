# [C] CVE-2019-10686

## Summary
Severity: Critical
Advisory: CVE-2019-10686
Aliases: GHSA-fvx3-g627-phm2
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-04-01
Source: https://osv.dev/vulnerability/CVE-2019-10686
Type: osv

## Details
An SSRF vulnerability was found in an API from Ctrip Apollo through 1.4.0-SNAPSHOT. An attacker may use it to do an intranet port scan or raise a GET request via /system-info/health because the %23 substring is mishandled.

## References
- https://github.com/ctripcorp/apollo/issues/2103
