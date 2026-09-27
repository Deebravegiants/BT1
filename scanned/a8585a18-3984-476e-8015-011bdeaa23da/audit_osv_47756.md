# [M] CVE-2017-11549

## Summary
Severity: Medium
Advisory: CVE-2017-11549
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/CVE-2017-11549
Type: osv

## Details
The play_midi function in playmidi.c in TiMidity++ 2.14.0 allows remote attackers to cause a denial of service (large loop and CPU consumption) via a crafted mid file. NOTE: CPU consumption might be relevant when using the --background option.

## References
- http://seclists.org/fulldisclosure/2017/Jul/83
