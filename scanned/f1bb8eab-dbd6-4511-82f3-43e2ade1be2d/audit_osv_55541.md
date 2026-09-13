# [M] CVE-2025-7462

## Summary
Severity: Medium
Advisory: CVE-2025-7462
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-07-12
Source: https://osv.dev/vulnerability/CVE-2025-7462
Type: osv

## Details
A vulnerability was found in Artifex GhostPDL up to 3989415a5b8e99b9d1b87cc9902bde9b7cdea145. It has been classified as problematic. This affects the function pdf_ferror of the file devices/vector/gdevpdf.c of the component New Output File Open Error Handler. The manipulation leads to null pointer dereference. It is possible to initiate the attack remotely. The identifier of the patch is 619a106ba4c4abed95110f84d5efcd7aee38c7cb. It is recommended to apply a patch to fix this issue.

## References
- https://artifex.com/
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=619a106ba4c4
- https://vuldb.com/?ctiid.316113
- https://vuldb.com/?id.316113
- https://vuldb.com/?submit.610173
