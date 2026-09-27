# [C] CVE-2017-5885

## Summary
Severity: Critical
Advisory: CVE-2017-5885
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-28
Source: https://osv.dev/vulnerability/CVE-2017-5885
Type: osv

## Details
Multiple integer overflows in the (1) vnc_connection_server_message and (2) vnc_color_map_set functions in gtk-vnc before 0.7.0 allow remote servers to cause a denial of service (crash) or possibly execute arbitrary code via vectors involving SetColorMapEntries, which triggers a buffer overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LGPQ5MQR6SN4DYTEFACHP2PP5RR26KYK/
- http://www.openwall.com/lists/oss-security/2017/02/03/5
- http://www.openwall.com/lists/oss-security/2017/02/05/5
- http://www.securityfocus.com/bid/96016
- https://access.redhat.com/errata/RHSA-2017:2258
- https://bugzilla.gnome.org/show_bug.cgi?id=778050
- https://git.gnome.org/browse/gtk-vnc/commit/?id=c8583fd3783c5b811590fcb7bae4ce6e7344963e
