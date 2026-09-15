# [H] CVE-2020-27638

## Summary
Severity: High
Advisory: CVE-2020-27638
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-22
Source: https://osv.dev/vulnerability/CVE-2020-27638
Type: osv

## Details
receive.c in fastd before v21 allows denial of service (assertion failure) when receiving packets with an invalid type code.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D2LNSF2LI4RQ7BVGHTJQUJWP7RVGHDTK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GUZ3AGTAXH7OOP45F5WXBVRQ3IDWUR7M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WSMH65GHKHMJAK2VMPROIPIUS4IA63CW/
- https://fastd.readthedocs.io/en/stable/releases/v21.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00025.html
- https://bugs.debian.org/972521
- https://github.com/NeoRaider/fastd/commit/737925113363b6130879729cdff9ccc46c33eaea
