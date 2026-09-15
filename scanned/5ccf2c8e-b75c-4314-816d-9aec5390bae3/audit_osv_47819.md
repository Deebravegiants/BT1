# [H] CVE-2017-12958

## Summary
Severity: High
Advisory: CVE-2017-12958
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12958
Type: osv

## Details
There is an illegal address access in the function output_hex() in data/data-out.c of the libpspp library in GNU PSPP before 1.0.1 that will lead to remote denial of service.

## References
- https://savannah.gnu.org/forum/forum.php?forum_id=8936
- https://bugzilla.redhat.com/show_bug.cgi?id=1482429
