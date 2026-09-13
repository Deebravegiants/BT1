# [H] CVE-2019-9923

## Summary
Severity: High
Advisory: CVE-2019-9923
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-22
Source: https://osv.dev/vulnerability/CVE-2019-9923
Type: osv

## Details
pax_decode_header in sparse.c in GNU Tar before 1.32 had a NULL pointer dereference when parsing certain archives that have malformed extended headers.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00077.html
- http://savannah.gnu.org/bugs/?55369
- http://git.savannah.gnu.org/cgit/tar.git/commit/?id=cb07844454d8cc9fb21f53ace75975f91185a120
- https://bugs.launchpad.net/ubuntu/+source/tar/+bug/1810241
