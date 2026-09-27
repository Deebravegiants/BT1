# [H] CVE-2017-17527

## Summary
Severity: High
Advisory: CVE-2017-17527
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17527
Type: osv

## Details
delphi_gui/WWWBrowserRunnerDM.pas in PasDoc 0.14 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL. NOTE: a software maintainer has indicated that the code referencing the BROWSER environment variable is never used

## References
- https://security-tracker.debian.org/tracker/CVE-2017-17527
