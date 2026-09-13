# [H] CVE-2018-1000658

## Summary
Severity: High
Advisory: CVE-2018-1000658
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-1000658
Type: osv

## Details
LimeSurvey version prior to 3.14.4 contains a file upload vulnerability in upload functionality that can result in an attacker gaining code execution via webshell. This attack appear to be exploitable via an authenticated user uploading a zip archive which can contains malicious php files that can be called under certain circumstances. This vulnerability appears to have been fixed in after commit 91d143230eb357260a19c8424b3005deb49a47f7 / version 3.14.4.

## References
- https://github.com/LimeSurvey/LimeSurvey/commit/20fc85edccc80e7e7f162613542792380c44446a
- https://github.com/LimeSurvey/LimeSurvey/commit/91d143230eb357260a19c8424b3005deb49a47f7
