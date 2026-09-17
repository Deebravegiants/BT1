# [H] CVE-2018-11710

## Summary
Severity: High
Advisory: CVE-2018-11710
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2018-11710
Type: osv

## Details
soundlib/pattern.h in libopenmpt before 0.3.9 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted AMS file because of an invalid write near address 0 in an out-of-memory situation.

## References
- https://source.openmpt.org/browse/openmpt/trunk/?op=revision&rev=10149&peg=10150
- https://lib.openmpt.org/libopenmpt/2018/04/29/security-updates-0.3.9-0.2-beta32-0.2.7561-beta20.5-p9-0.2.7386-beta20.3-p12/
