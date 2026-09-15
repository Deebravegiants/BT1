# [H] CVE-2018-11225

## Summary
Severity: High
Advisory: CVE-2018-11225
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/CVE-2018-11225
Type: osv

## Details
The dcputs function in decompile.c in libming through 0.4.8 mishandles cases where the header indicates a file size greater than the actual size, which allows remote attackers to cause a denial of service (Segmentation fault and application crash) or possibly have unspecified other impact.

## References
- https://docs.google.com/document/d/1gTd44AjxkCNkoDDh28NwiSeLDa5poBYROEoLEG4JVCA/edit
- https://github.com/libming/libming/issues/143
