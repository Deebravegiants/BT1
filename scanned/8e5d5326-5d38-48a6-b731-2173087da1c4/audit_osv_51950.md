# [M] CVE-2021-46238

## Summary
Severity: Medium
Advisory: CVE-2021-46238
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-46238
Type: osv

## Details
GPAC v1.1.0 was discovered to contain a stack overflow via the function gf_node_get_name () at scenegraph/base_scenegraph.c. This vulnerability can lead to a program crash, causing a Denial of Service (DoS).

## References
- https://github.com/gpac/gpac/issues/2027
