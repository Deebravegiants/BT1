# [H] JLSEC-2026-138

## Summary
Severity: High
Advisory: JLSEC-2026-138
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-138
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.4.4+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. In versions 3.2.0 through 3.2.4, 3.3.0 through 3.3.5, and 3.4.0 through 3.4.2, a memory safety bug in the legacy OpenEXR Python adapter (the deprecated OpenEXR.InputFile wrapper) allow crashes and likely code execution when opening attacker-controlled EXR files or when passing crafted Python objects. Integer overflow and unchecked allocation in InputFile.channel() and InputFile.channels() can lead to heap overflow (32 bit) or a NULL deref (64 bit). Versions 3.2.5, 3.3.6, and 3.4.3 contain a patch for the issue.

## References
- https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L528-L536
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-vh63-9mqx-wmjr
