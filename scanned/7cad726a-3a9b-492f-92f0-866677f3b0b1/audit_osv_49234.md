# [C] CVE-2018-7263

## Summary
Severity: Critical
Advisory: CVE-2018-7263
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-20
Source: https://osv.dev/vulnerability/CVE-2018-7263
Type: osv

## Details
The mad_decoder_run() function in decoder.c in Underbit libmad through 0.15.1b allows remote attackers to cause a denial of service (SIGABRT because of double free or corruption) or possibly have unspecified other impact via a crafted file. NOTE: this may overlap CVE-2017-11552.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870608
- https://bugzilla.suse.com/show_bug.cgi?id=1081784
