# [C] CVE-2015-0855

## Summary
Severity: Critical
Advisory: CVE-2015-0855
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2015-0855
Type: osv

## Details
The _mediaLibraryPlayCb function in mainwindow.py in pitivi before 0.95 allows attackers to execute arbitrary code via shell metacharacters in a file path.

## References
- http://www.openwall.com/lists/oss-security/2015/12/23/8
- https://bugs.launchpad.net/ubuntu/+source/pitivi/+bug/1495272
- https://git.gnome.org/browse/pitivi/commit/?id=45a4c84edb3b4343f199bba1c65502e3f49f5bb2
- http://www.openwall.com/lists/oss-security/2015/12/23/8
- http://www.openwall.com/lists/oss-security/2015/12/23/8
- https://git.gnome.org/browse/pitivi/commit/?id=45a4c84edb3b4343f199bba1c65502e3f49f5bb2
- https://bugs.launchpad.net/ubuntu/+source/pitivi/+bug/1495272
- https://git.gnome.org/browse/pitivi/commit/?id=45a4c84edb3b4343f199bba1c65502e3f49f5bb2
- http://www.securityfocus.com/bid/97283
