# [H] CVE-2023-1448

## Summary
Severity: High
Advisory: CVE-2023-1448
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-17
Source: https://osv.dev/vulnerability/CVE-2023-1448
Type: osv

## Details
A vulnerability, which was classified as problematic, was found in GPAC 2.3-DEV-rev35-gbbca86917-master. This affects the function gf_m2ts_process_sdt of the file media_tools/mpegts.c. The manipulation leads to heap-based buffer overflow. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue. The identifier VDB-223293 was assigned to this vulnerability.

## References
- https://vuldb.com/?id.223293
- https://github.com/gpac/gpac/issues/2388
- https://vuldb.com/?ctiid.223293
- https://github.com/xxy1126/Vuln/blob/main/gpac/3
