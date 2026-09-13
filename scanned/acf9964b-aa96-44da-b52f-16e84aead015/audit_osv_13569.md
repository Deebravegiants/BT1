# [M] CVE-2018-20357

## Summary
Severity: Medium
Advisory: CVE-2018-20357
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-22
Source: https://osv.dev/vulnerability/CVE-2018-20357
Type: osv

## Details
A NULL pointer dereference was discovered in sbr_process_channel of libfaad/sbr_dec.c in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. The vulnerability causes a segmentation fault and application crash.

## References
- https://seclists.org/bugtraq/2019/Sep/28
- https://security.gentoo.org/glsa/202006-17
- https://www.debian.org/security/2019/dsa-4522
- https://github.com/knik0/faad2/issues/28
