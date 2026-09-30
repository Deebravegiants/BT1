# [H] CVE-2019-12212

## Summary
Severity: High
Advisory: CVE-2019-12212
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12212
Type: osv

## Details
When FreeImage 3.18.0 reads a special JXR file, the StreamCalcIFDSize function of JXRMeta.c repeatedly calls itself due to improper processing of the file, eventually causing stack exhaustion. An attacker can achieve a remote denial of service attack by sending a specially constructed file.

## References
- https://sourceforge.net/p/freeimage/discussion/36111/thread/e06734bed5/
