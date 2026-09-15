# [H] CVE-2018-1000100

## Summary
Severity: High
Advisory: CVE-2018-1000100
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-1000100
Type: osv

## Details
GPAC MP4Box version 0.7.1 and earlier contains a Buffer Overflow vulnerability in src/isomedia/avc_ext.c lines 2417 to 2420 that can result in Heap chunks being modified, this could lead to RCE. This attack appear to be exploitable via an attacker supplied MP4 file that when run by the victim may result in RCE.

## References
- https://github.com/gpac/gpac/issues/994
- https://usn.ubuntu.com/3926-1/
