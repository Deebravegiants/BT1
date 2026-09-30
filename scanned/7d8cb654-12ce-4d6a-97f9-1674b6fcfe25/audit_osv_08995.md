# [H] CVE-2016-7164

## Summary
Severity: High
Advisory: CVE-2016-7164
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2016-7164
Type: osv

## Details
The construct function in puff.cpp in Libtorrent 1.1.0 allows remote torrent trackers to cause a denial of service (segmentation fault and crash) via a crafted GZIP response.

## References
- http://www.securityfocus.com/bid/92891
- http://www.openwall.com/lists/oss-security/2016/09/08/1
- http://www.openwall.com/lists/oss-security/2016/09/08/7
- https://github.com/arvidn/libtorrent/issues/1021
- https://github.com/arvidn/libtorrent/pull/1022
