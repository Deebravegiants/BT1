# [H] CVE-2017-11661

## Summary
Severity: High
Advisory: CVE-2017-11661
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-17
Source: https://osv.dev/vulnerability/CVE-2017-11661
Type: osv

## Details
The _WM_SetupMidiEvent function in internal_midi.c:2318 in WildMIDI 0.4.2 can cause a denial of service (invalid memory read and application crash) via a crafted mid file.

## References
- http://seclists.org/fulldisclosure/2017/Aug/12
- https://www.exploit-db.com/exploits/42433/
