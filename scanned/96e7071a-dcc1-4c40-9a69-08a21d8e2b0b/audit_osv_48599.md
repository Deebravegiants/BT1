# [M] CVE-2018-0501

## Summary
Severity: Medium
Advisory: CVE-2018-0501
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-0501
Type: osv

## Details
The mirror:// method implementation in Advanced Package Tool (APT) 1.6.x before 1.6.4 and 1.7.x before 1.7.0~alpha3 mishandles gpg signature verification for the InRelease file of a fallback mirror, aka mirrorfail.

## References
- https://usn.ubuntu.com/3746-1/
- https://mirror.fail
- https://salsa.debian.org/apt-team/apt/commit/29658a3a74af49e2a24e17bdebb20e1612aac3ec
- https://salsa.debian.org/apt-team/apt/commit/aebd4278bacc728ab00ebe31556983e140f60e47
