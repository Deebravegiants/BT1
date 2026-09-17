# [M] CVE-2016-3178

## Summary
Severity: Medium
Advisory: CVE-2016-3178
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-3178
Type: osv

## Details
The processRequest function in minissdpd.c in MiniSSDPd 1.2.20130907-3 allows local users to cause a denial of service (out-of-bounds memory access and daemon crash) via vectors involving a negative length value.

## References
- http://speirofr.appspot.com/files/advisory/SPADV-2016-02.md
- http://www.openwall.com/lists/oss-security/2016/03/16/13
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=816759
- https://github.com/miniupnp/miniupnp/commit/b238cade9a173c6f751a34acf8ccff838a62aa47
