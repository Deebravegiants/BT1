# [M] CVE-2021-46311

## Summary
Severity: Medium
Advisory: CVE-2021-46311
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-46311
Type: osv

## Details
A NULL pointer dereference vulnerability exists in GPAC v1.1.0 via the function gf_sg_destroy_routes () at scenegraph/vrml_route.c. This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/gpac/gpac/issues/2038
