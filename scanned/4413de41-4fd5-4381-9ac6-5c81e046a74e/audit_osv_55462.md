# [C] GHSL-2025-042: Poppler has Use-After-Free

## Summary
Severity: Critical
Advisory: CVE-2025-52885
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/CVE-2025-52885
Type: osv

## Details
Poppler ia a library for rendering PDF files, and examining or modifying their structure. A use-after-free (write) vulnerability has been detected in versions Poppler prior to 25.10.0 within the StructTreeRoot class. The issue arises from the use of raw pointers to elements of a `std::vector`, which can lead to dangling pointers when the vector is resized. The vulnerability stems from the way that refToParentMap stores references to `std::vector` elements using raw pointers. These pointers may become invalid when the vector is resized. This vulnerability is a common security problem involving the use of raw pointers to `std::vectors`. Internally, `std::vector `stores its elements in a dynamically allocated array. When the array reaches its capacity and a new element is added, the vector reallocates a larger block of memory and moves all the existing elements to the new location. At this point if any pointers to elements are stored before a resize occurs, they become dangling pointers once the reallocation happens. Version 25.10.0 contains a patch for the issue.

## References
- https://securitylab.github.com/advisories/GHSL-2025-042_poppler/
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1884
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1884#note_3114334
