# [C] CVE-2017-7375

## Summary
Severity: Critical
Advisory: CVE-2017-7375
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2017-7375
Type: osv

## Details
A flaw in libxml2 allows remote XML entity inclusion with default parser flags (i.e., when the caller did not request entity substitution, DTD validation, external DTD subset loading, or default DTD attributes). Depending on the context, this may expose a higher-risk attack surface in libxml2 not usually reachable with default parser flags, and expose content from local files, HTTP, or FTP servers (which might be otherwise unreachable).

## References
- http://www.securityfocus.com/bid/98877
- http://www.securitytracker.com/id/1038623
- https://security.gentoo.org/glsa/201711-01
- https://www.debian.org/security/2017/dsa-3952
- https://android.googlesource.com/platform/external/libxml2/+/308396a55280f69ad4112d4f9892f4cbeff042aa
- https://bugzilla.redhat.com/show_bug.cgi?id=1462203
- https://git.gnome.org/browse/libxml2/commit/?id=90ccb58242866b0ba3edbef8fe44214a101c2b3e
- https://source.android.com/security/bulletin/2017-06-01
