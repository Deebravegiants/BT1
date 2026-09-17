# [M] CVE-2020-10754

## Summary
Severity: Medium
Advisory: CVE-2020-10754
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-10754
Type: osv

## Details
It was found that nmcli, a command line interface to NetworkManager did not honour 802-1x.ca-path and 802-1x.phase2-ca-path settings, when creating a new profile. When a user connects to a network using this profile, the authentication does not happen and the connection is made insecurely.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/44FTVXWKDYIAMOOP2PZMUY3D2QNWAVBZ/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10754
