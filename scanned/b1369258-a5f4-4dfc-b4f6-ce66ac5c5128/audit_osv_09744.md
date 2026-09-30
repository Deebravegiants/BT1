# [H] CVE-2017-11311

## Summary
Severity: High
Advisory: CVE-2017-11311
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11311
Type: osv

## Details
soundlib/Load_psm.cpp in OpenMPT through 1.26.12.00 and libopenmpt before 0.2.8461-beta26 has a heap buffer overflow with the potential for arbitrary code execution via a crafted PSM File that triggers use of the same sample slot for two samples.

## References
- https://bugs.debian.org/867579
- https://lib.openmpt.org/libopenmpt/md_announce-2017-07-07.html
- https://source.openmpt.org/browse/openmpt/branches/OpenMPT-1.26/?op=revision&rev=8438
- https://source.openmpt.org/browse/openmpt/trunk/?rev=6800
