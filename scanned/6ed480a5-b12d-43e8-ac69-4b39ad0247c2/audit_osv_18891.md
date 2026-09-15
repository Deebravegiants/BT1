# [C] CVE-2020-36773

## Summary
Severity: Critical
Advisory: CVE-2020-36773
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-04
Source: https://osv.dev/vulnerability/CVE-2020-36773
Type: osv

## Details
Artifex Ghostscript before 9.53.0 has an out-of-bounds write and use-after-free in devices/vector/gdevtxtw.c (for txtwrite) because a single character code in a PDF document can map to more than one Unicode code point (e.g., for a ligature).

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=8c7bd787defa071c96289b7da9397f673fddb874
- https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/tag/gs9530
- https://bugzilla.opensuse.org/show_bug.cgi?id=1177922
- https://bugs.ghostscript.com/show_bug.cgi?id=702229
