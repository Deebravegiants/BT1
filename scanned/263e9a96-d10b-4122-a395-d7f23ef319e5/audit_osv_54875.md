# [H] CVE-2024-55195

## Summary
Severity: High
Advisory: CVE-2024-55195
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-23
Source: https://osv.dev/vulnerability/CVE-2024-55195
Type: osv

## Details
An allocation-size-too-big bug in the component /imagebuf.cpp of OpenImageIO v3.1.0.0dev may cause a Denial of Service (DoS) when the program to requests to allocate too much space.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/issues/4553
