# [M] CVE-2020-1983

## Summary
Severity: Medium
Advisory: CVE-2020-1983
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-04-22
Source: https://osv.dev/vulnerability/CVE-2020-1983
Type: osv

## Details
A use after free vulnerability in ip_reass() in ip_input.c of libslirp 4.2.0 and prior releases allows crafted packets to cause a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HWFD4MWV3YWIHVHSA2F7FKOLJFL4PHOX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NKT2MTSINE4NUPG5L6BYH6N23NBNITOL/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00020.html
- https://usn.ubuntu.com/4372-1/
- https://www.debian.org/security/2020/dsa-4665
- https://gitlab.freedesktop.org/slirp/libslirp/-/commit/9ac0371bb8c0a40f5d9f82a1c25129660e81df04
- https://gitlab.freedesktop.org/slirp/libslirp/-/issues/20
