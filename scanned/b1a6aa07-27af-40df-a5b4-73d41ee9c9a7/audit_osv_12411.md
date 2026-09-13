# [H] CVE-2018-11740

## Summary
Severity: High
Advisory: CVE-2018-11740
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-11740
Type: osv

## Details
An issue was discovered in libtskbase.a in The Sleuth Kit (TSK) from release 4.0.2 through to 4.6.1. An out-of-bounds read of a memory region was found in the function tsk_UTF16toUTF8 in tsk/base/tsk_unicode.c which could be leveraged by an attacker to disclose information or manipulated to read from unmapped memory causing a denial of service attack.

## References
- https://github.com/sleuthkit/sleuthkit/issues/1264
