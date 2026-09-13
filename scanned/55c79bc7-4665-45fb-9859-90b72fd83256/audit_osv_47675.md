# [H] CVE-2017-0374

## Summary
Severity: High
Advisory: CVE-2017-0374
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-0374
Type: osv

## Details
lib/Config/Model.pm in Config-Model (aka libconfig-model-perl) before 2.102 allows local users to gain privileges via a crafted model in the current working directory, related to use of . with the INC array.

## References
- http://cpansearch.perl.org/src/DDUMONT/Config-Model-2.102/Changes
- https://security-tracker.debian.org/tracker/CVE-2017-0374
- https://anonscm.debian.org/cgit/pkg-perl/packages/libconfig-model-perl.git/commit/?h=stretch&id=0de8471e5a8958ad37446dfcd0362a269e3ec573
