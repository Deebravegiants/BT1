# [H] CVE-2017-13735

## Summary
Severity: High
Advisory: CVE-2017-13735
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13735
Type: osv

## Details
There is a floating point exception in the kodak_radc_load_raw function in dcraw_common.cpp in LibRaw 0.18.2. It will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1483988
