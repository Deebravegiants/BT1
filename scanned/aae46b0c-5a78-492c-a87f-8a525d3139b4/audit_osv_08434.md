# [M] CVE-2016-3179

## Summary
Severity: Medium
Advisory: CVE-2016-3179
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-3179
Type: osv

## Details
The processRequest function in minissdpd.c in MiniSSDPd 1.2.20130907-3 allows local users to cause a denial of service (invalid free and daemon crash) via vectors related to error handling.

## References
- http://speirofr.appspot.com/files/advisory/SPADV-2016-02.md
- http://www.openwall.com/lists/oss-security/2016/03/16/13
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=816759
- https://github.com/miniupnp/miniupnp/commit/140ee8d2204b383279f854802b27bdb41c1d5d1a
