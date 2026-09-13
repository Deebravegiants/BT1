# [M] CVE-2018-10017

## Summary
Severity: Medium
Advisory: CVE-2018-10017
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-11
Source: https://osv.dev/vulnerability/CVE-2018-10017
Type: osv

## Details
soundlib/Snd_fx.cpp in OpenMPT before 1.27.07.00 and libopenmpt before 0.3.8 allows remote attackers to cause a denial of service (out-of-bounds read) via an IT or MO3 file with many nested pattern loops.

## References
- https://openmpt.org/openmpt-1-27-07-00-released
- https://github.com/OpenMPT/openmpt/commit/7ebf02af2e90f03e0dbd0e18b8b3164f372fb97c
- https://lib.openmpt.org/libopenmpt/2018/04/08/security-updates-0.3.8-0.2-beta31-0.2.7561-beta20.5-p8-0.2.7386-beta20.3-p11/
