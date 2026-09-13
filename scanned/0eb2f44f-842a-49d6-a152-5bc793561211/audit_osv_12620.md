# [M] CVE-2018-13440

## Summary
Severity: Medium
Advisory: CVE-2018-13440
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-08
Source: https://osv.dev/vulnerability/CVE-2018-13440
Type: osv

## Details
The audiofile Audio File Library 0.3.6 has a NULL pointer dereference bug in ModuleState::setup in modules/ModuleState.cpp, which allows an attacker to cause a denial of service via a crafted caf file, as demonstrated by sfconvert.

## References
- https://usn.ubuntu.com/3800-1/
- https://github.com/mpruett/audiofile/issues/49
