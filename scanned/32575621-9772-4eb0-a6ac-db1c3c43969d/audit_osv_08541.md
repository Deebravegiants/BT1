# [H] CVE-2016-4330

## Summary
Severity: High
Advisory: CVE-2016-4330
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2016-11-18
Source: https://osv.dev/vulnerability/CVE-2016-4330
Type: osv

## Details
In the HDF5 1.8.16 library's failure to check if the number of dimensions for an array read from the file is within the bounds of the space allocated for it, a heap-based buffer overflow will occur, potentially leading to arbitrary code execution.

## References
- http://www.securityfocus.com/bid/94414
- http://www.debian.org/security/2016/dsa-3727
- https://security.gentoo.org/glsa/201701-13
- http://www.talosintelligence.com/reports/TALOS-2016-0176/
