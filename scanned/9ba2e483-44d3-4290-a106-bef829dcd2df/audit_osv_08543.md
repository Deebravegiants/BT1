# [H] CVE-2016-4332

## Summary
Severity: High
Advisory: CVE-2016-4332
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2016-11-18
Source: https://osv.dev/vulnerability/CVE-2016-4332
Type: osv

## Details
The library's failure to check if certain message types support a particular flag, the HDF5 1.8.16 library will cast the structure to an alternative structure and then assign to fields that aren't supported by the message type and the library will write outside the bounds of the heap buffer. This can lead to code execution under the context of the library.

## References
- http://www.securityfocus.com/bid/94417
- http://www.debian.org/security/2016/dsa-3727
- https://security.gentoo.org/glsa/201701-13
- http://www.talosintelligence.com/reports/TALOS-2016-0178/
