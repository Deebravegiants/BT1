# [H] CVE-2018-0429

## Summary
Severity: High
Advisory: CVE-2018-0429
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-09
Source: https://osv.dev/vulnerability/CVE-2018-0429
Type: osv

## Details
Stack-based buffer overflow in the Cisco Thor decoder before commit 18de8f9f0762c3a542b1122589edb8af859d9813 allows local users to cause a denial of service (segmentation fault) and execute arbitrary code via a crafted non-conformant Thor bitstream.

## References
- http://www.securityfocus.com/bid/105059
- https://github.com/cisco/thor/commit/18de8f9f0762c3a542b1122589edb8af859d9813
