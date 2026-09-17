# [H] CVE-2023-1449

## Summary
Severity: High
Advisory: CVE-2023-1449
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-17
Source: https://osv.dev/vulnerability/CVE-2023-1449
Type: osv

## Details
A vulnerability has been found in GPAC 2.3-DEV-rev35-gbbca86917-master and classified as problematic. This vulnerability affects the function gf_av1_reset_state of the file media_tools/av_parsers.c. The manipulation leads to double free. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue. VDB-223294 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?id.223294
- https://vuldb.com/?ctiid.223294
- https://github.com/gpac/gpac/issues/2387
- https://github.com/xxy1126/Vuln/blob/main/gpac/2
