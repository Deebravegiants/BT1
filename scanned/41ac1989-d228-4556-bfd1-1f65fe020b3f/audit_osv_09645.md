# [H] CVE-2017-1000494

## Summary
Severity: High
Advisory: CVE-2017-1000494
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-1000494
Type: osv

## Details
Uninitialized stack variable vulnerability in NameValueParserEndElt (upnpreplyparse.c) in miniupnpd < 2.0 allows an attacker to cause Denial of Service (Segmentation fault and Memory Corruption) or possibly have unspecified other impact

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00045.html
- https://usn.ubuntu.com/3562-1/
- https://github.com/miniupnp/miniupnp/issues/268
- https://github.com/miniupnp/miniupnp/commit/7aeb624b44f86d335841242ff427433190e7168a
