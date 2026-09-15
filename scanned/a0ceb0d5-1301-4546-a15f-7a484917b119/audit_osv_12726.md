# [M] CVE-2018-14524

## Summary
Severity: Medium
Advisory: CVE-2018-14524
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-14524
Type: osv

## Details
dwg_decode_eed in decode.c in GNU LibreDWG before 0.6 leads to a double free (in dwg_free_eed in free.c) because it does not properly manage the obj->eed value after a free occurs.

## References
- https://github.com/LibreDWG/libredwg/issues/33
- https://savannah.gnu.org/forum/forum.php?forum_id=9211
