# [H] CVE-2018-11017

## Summary
Severity: High
Advisory: CVE-2018-11017
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-13
Source: https://osv.dev/vulnerability/CVE-2018-11017
Type: osv

## Details
The newVar_N function in decompile.c in libming through 0.4.8 mishandles cases where the header indicates a file size greater than the actual size, which allows remote attackers to cause a denial of service (Segmentation fault and application crash) or possibly have unspecified other impact.

## References
- https://docs.google.com/document/d/18lJc_F5p3HPaMwsUAIwP0zMMhwJs-Snhuj05nhMIgAw/edit
