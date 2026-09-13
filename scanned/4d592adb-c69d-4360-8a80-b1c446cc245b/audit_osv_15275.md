# [C] CVE-2019-14906

## Summary
Severity: Critical
Advisory: CVE-2019-14906
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-07
Source: https://osv.dev/vulnerability/CVE-2019-14906
Type: osv

## Details
A flaw was found with the RHSA-2019:3950 erratum, where it did not fix the CVE-2019-13616 SDL vulnerability. This issue only affects Red Hat SDL packages, SDL versions through 1.2.15 and 2.x through 2.0.9 has a heap-based buffer overflow flaw while copying an existing surface into a new optimized one, due to a lack of validation while loading a BMP image, is possible. An application that uses SDL to parse untrusted input files may be vulnerable to this flaw, which could allow an attacker to make the application crash or execute code.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14906
