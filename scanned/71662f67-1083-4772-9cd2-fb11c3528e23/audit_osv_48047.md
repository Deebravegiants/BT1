# [H] CVE-2017-17529

## Summary
Severity: High
Advisory: CVE-2017-17529
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17529
Type: osv

## Details
af/util/xp/ut_go_file.cpp in AbiWord 3.0.2-2 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL.

## References
- https://security-tracker.debian.org/tracker/CVE-2017-17529
