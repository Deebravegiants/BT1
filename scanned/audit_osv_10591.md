# [H] CVE-2017-17522

## Summary
Severity: High
Advisory: CVE-2017-17522
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17522
Type: osv

## Details
Lib/webbrowser.py in Python through 3.6.3 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL. NOTE: a software maintainer indicates that exploitation is impossible because the code relies on subprocess.Popen and the default shell=False setting

## References
- https://bugs.python.org/issue32367
- http://www.securityfocus.com/bid/102207
- https://security-tracker.debian.org/tracker/CVE-2017-17522
