# [H] CVE-2016-4331

## Summary
Severity: High
Advisory: CVE-2016-4331
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2016-11-18
Source: https://osv.dev/vulnerability/CVE-2016-4331
Type: osv

## Details
When decoding data out of a dataset encoded with the H5Z_NBIT decoding, the HDF5 1.8.16 library will fail to ensure that the precision is within the bounds of the size leading to arbitrary code execution.

## References
- http://www.securityfocus.com/bid/94411
- http://www.debian.org/security/2016/dsa-3727
- https://security.gentoo.org/glsa/201701-13
- http://www.talosintelligence.com/reports/TALOS-2016-0177/
