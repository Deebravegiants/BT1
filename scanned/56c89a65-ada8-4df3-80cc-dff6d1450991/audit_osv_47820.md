# [H] CVE-2017-12959

## Summary
Severity: High
Advisory: CVE-2017-12959
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12959
Type: osv

## Details
There is a reachable assertion abort in the function dict_add_mrset() in data/dictionary.c of the libpspp library in GNU PSPP before 1.0.1 that will lead to a remote denial of service attack.

## References
- https://savannah.gnu.org/forum/forum.php?forum_id=8936
- https://bugzilla.redhat.com/show_bug.cgi?id=1482432
