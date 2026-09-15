# [C] CVE-2019-17113

## Summary
Severity: Critical
Advisory: CVE-2019-17113
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-04
Source: https://osv.dev/vulnerability/CVE-2019-17113
Type: osv

## Details
In libopenmpt before 0.3.19 and 0.4.x before 0.4.9, ModPlug_InstrumentName and ModPlug_SampleName in libopenmpt_modplug.c do not restrict the lengths of libmodplug output-buffer strings in the C API, leading to a buffer overflow.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00044.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00003.html
- https://www.debian.org/security/2020/dsa-4729
- https://github.com/OpenMPT/openmpt/commit/927688ddab43c2b203569de79407a899e734fabe
- https://github.com/OpenMPT/openmpt/compare/libopenmpt-0.3.18...libopenmpt-0.3.19
- https://github.com/OpenMPT/openmpt/compare/libopenmpt-0.4.8...libopenmpt-0.4.9
- https://source.openmpt.org/browse/openmpt/trunk/OpenMPT/?op=revision&rev=12127&peg=12127
