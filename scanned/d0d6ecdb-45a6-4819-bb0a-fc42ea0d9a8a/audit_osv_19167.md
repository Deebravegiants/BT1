# [C] CVE-2020-8432

## Summary
Severity: Critical
Advisory: CVE-2020-8432
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/CVE-2020-8432
Type: osv

## Details
In Das U-Boot through 2020.01, a double free has been found in the cmd/gpt.c do_rename_gpt_parts() function. Double freeing may result in a write-what-where condition, allowing an attacker to execute arbitrary code. NOTE: this vulnerablity was introduced when attempting to fix a memory leak identified by static analysis.

## References
- https://www.mail-archive.com/u-boot%40lists.denx.de/msg354060.html
- https://www.mail-archive.com/u-boot%40lists.denx.de/msg354114.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00030.html
