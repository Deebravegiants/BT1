# [H] CVE-2017-17514

## Summary
Severity: High
Advisory: CVE-2017-17514
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17514
Type: osv

## Details
boxes.c in nip2 8.4.0 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL. NOTE: a software maintainer indicates that this product does not use the BROWSER environment variable

## References
- https://github.com/jcupitt/nip2/issues/70
- https://security-tracker.debian.org/tracker/CVE-2017-17514
