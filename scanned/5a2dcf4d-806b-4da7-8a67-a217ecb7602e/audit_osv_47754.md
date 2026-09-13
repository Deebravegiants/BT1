# [M] CVE-2017-11547

## Summary
Severity: Medium
Advisory: CVE-2017-11547
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/CVE-2017-11547
Type: osv

## Details
The resample_gauss function in resample.c in TiMidity++ 2.14.0 allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted mid file. NOTE: a crash might be relevant when using the --background option. NOTE: the TiMidity++ README.alsaseq documentation suggests a setuid-root installation.

## References
- http://seclists.org/fulldisclosure/2017/Jul/83
