# [M] JLSEC-2026-139

## Summary
Severity: Medium
Advisory: JLSEC-2026-139
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-139
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.4.4+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. In versions 3.2.0 through 3.2.4, 3.3.0 through 3.3.5, and 3.4.0 through 3.4.2, there is a use-after-free in `PyObject_StealAttrString` of `pyOpenEXR_old.cpp`. The legacy adapter defines `PyObject_StealAttrString` that calls `PyObject_GetAttrString` to obtain a new reference, immediately decrefs it, and returns the pointer. Callers then pass this dangling pointer to APIs like `PyLong_AsLong/PyFloat_AsDouble`, resulting in a use-after-free. This is invoked in multiple places (e.g., reading PixelType.v, Box2i, V2f, etc.) Versions 3.2.5, 3.3.6, and 3.4.3 fix the issue.

## References
- https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L109-L115
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-57cw-j6vp-2p9m
