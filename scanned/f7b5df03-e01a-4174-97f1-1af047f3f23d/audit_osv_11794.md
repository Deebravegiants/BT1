# [M] CVE-2017-9762

## Summary
Severity: Medium
Advisory: CVE-2017-9762
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9762
Type: osv

## Details
The cmd_info function in libr/core/cmd_info.c in radare2 1.5.0 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted binary file.

## References
- http://www.securityfocus.com/bid/99140
- https://github.com/radare/radare2/issues/7726
