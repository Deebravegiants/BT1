# [M] CVE-2017-11664

## Summary
Severity: Medium
Advisory: CVE-2017-11664
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-17
Source: https://osv.dev/vulnerability/CVE-2017-11664
Type: osv

## Details
The _WM_SetupMidiEvent function in internal_midi.c:2122 in WildMIDI 0.4.2 can cause a denial of service (invalid memory read and application crash) via a crafted mid file.

## References
- https://github.com/Mindwerks/wildmidi/commit/ad6d7cf88d6673167ca1f517248af9409a9f1be1
- http://seclists.org/fulldisclosure/2017/Aug/12
- https://www.exploit-db.com/exploits/42433/
