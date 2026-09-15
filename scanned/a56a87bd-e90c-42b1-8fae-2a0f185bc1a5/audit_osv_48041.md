# [H] CVE-2017-17515

## Summary
Severity: High
Advisory: CVE-2017-17515
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17515
Type: osv

## Details
etc/ObjectList in Metview 4.7.3 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL. NOTE: a third party has indicated that the code to access this environment variable is not enabled in the shipped product

## References
- https://security-tracker.debian.org/tracker/CVE-2017-17515
