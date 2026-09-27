# [M] CVE-2020-6750

## Summary
Severity: Medium
Advisory: CVE-2020-6750
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-01-09
Source: https://osv.dev/vulnerability/CVE-2020-6750
Type: osv

## Details
GSocketClient in GNOME GLib through 2.62.4 may occasionally connect directly to a target address instead of connecting via a proxy server when configured to do so, because the proxy_addr field is mishandled. This bug is timing-dependent and may occur only sporadically depending on network delays. The greatest security relevance is in use cases where a proxy is used to help with privacy/anonymity, even though there is no technical barrier to a direct connection. NOTE: versions before 2.60 are unaffected.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5RIFEDSRJ4P3WFCMDUOFQ2LEILZLMDW7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KJMLGW55HOQXHMTIPH2PWXFRBNBWVO4W/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MEM7MMAXMWCDPUH4MTUZ763MBB64RRLJ/
- https://security.netapp.com/advisory/ntap-20200127-0001/
- https://bugzilla.suse.com/show_bug.cgi?id=1160668
- https://gitlab.gnome.org/GNOME/glib/issues/1989
