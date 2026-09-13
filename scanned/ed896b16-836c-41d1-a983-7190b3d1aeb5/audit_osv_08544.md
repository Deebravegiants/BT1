# [H] CVE-2016-4333

## Summary
Severity: High
Advisory: CVE-2016-4333
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2016-11-18
Source: https://osv.dev/vulnerability/CVE-2016-4333
Type: osv

## Details
The HDF5 1.8.16 library allocating space for the array using a value from the file has an impact within the loop for initializing said array allowing a value within the file to modify the loop's terminator. Due to this, an aggressor can cause the loop's index to point outside the bounds of the array when initializing it.

## References
- http://www.securityfocus.com/bid/94416
- http://www.debian.org/security/2016/dsa-3727
- https://security.gentoo.org/glsa/201701-13
- http://www.talosintelligence.com/reports/TALOS-2016-0179/
