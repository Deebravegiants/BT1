# [H] CVE-2017-17531

## Summary
Severity: High
Advisory: CVE-2017-17531
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17531
Type: osv

## Details
gozilla.c in GNU GLOBAL 4.8.6 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL.

## References
- https://security.gentoo.org/glsa/202008-02
- https://security-tracker.debian.org/tracker/CVE-2017-17531
