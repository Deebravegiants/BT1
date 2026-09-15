# [C] CVE-2020-35605

## Summary
Severity: Critical
Advisory: CVE-2020-35605
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-21
Source: https://osv.dev/vulnerability/CVE-2020-35605
Type: osv

## Details
The Graphics Protocol feature in graphics.c in kitty before 0.19.3 allows remote attackers to execute arbitrary code because a filename containing special characters can be included in an error message.

## References
- https://www.debian.org/security/2020/dsa-4819
- https://github.com/kovidgoyal/kitty/issues/3128
- https://github.com/kovidgoyal/kitty/commit/82c137878c2b99100a3cdc1c0f0efea069313901
