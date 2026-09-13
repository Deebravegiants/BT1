# [M] CVE-2019-20446

## Summary
Severity: Medium
Advisory: CVE-2019-20446
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-02-02
Source: https://osv.dev/vulnerability/CVE-2019-20446
Type: osv

## Details
In xml.rs in GNOME librsvg before 2.46.2, a crafted SVG file with nested patterns can cause denial of service when passed to the library for processing. The attacker constructs pattern elements so that the number of final rendered objects grows exponentially.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6IOHSO6BUKC6I66J5PZOMAGFVJ66ZS57/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X3B5RWJQD5LA45MYLLR55KZJOJ5NVZGP/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00024.html
- https://gitlab.gnome.org/GNOME/librsvg/issues/515
- https://lists.debian.org/debian-lts-announce/2020/07/msg00016.html
- https://security.netapp.com/advisory/ntap-20221111-0004/
- https://usn.ubuntu.com/4436-1/
