# [C] JLSEC-2026-89

## Summary
Severity: Critical
Advisory: JLSEC-2026-89
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-89
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <25.10.0+0

## Details
Poppler ia a library for rendering PDF files, and examining or modifying their structure. A use-after-free (write) vulnerability has been detected in versions Poppler prior to 25.10.0 within the StructTreeRoot class. The issue arises from the use of raw pointers to elements of a `std::vector`, which can lead to dangling pointers when the vector is resized. The vulnerability stems from the way that refToParentMap stores references to `std::vector` elements using raw pointers. These pointers may become invalid when the vector is resized. This vulnerability is a common security problem involving the use of raw pointers to `std::vectors`. Internally, `std::vector `stores its elements in a dynamically allocated array. When the array reaches its capacity and a new element is added, the vector reallocates a larger block of memory and moves all the existing elements to the new location. At this point if any pointers to elements are stored before a resize occurs, they become dangling pointers once the reallocation happens. Version 25.10.0 contains a patch for the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/10/13/2
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1884
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1884#note_3114334
- https://securitylab.github.com/advisories/GHSL-2025-042_poppler/
