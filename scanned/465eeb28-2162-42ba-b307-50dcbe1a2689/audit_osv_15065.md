# [H] CVE-2019-13178

## Summary
Severity: High
Advisory: CVE-2019-13178
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-02
Source: https://osv.dev/vulnerability/CVE-2019-13178
Type: osv

## Details
modules/luksbootkeyfile/main.py in Calamares versions 3.1 through 3.2.10 has a race condition between the time when the LUKS encryption keyfile is created and when secure permissions are set.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q57BOTBA2J5U4GVKUP7N2PD5H7B3BVUU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R2ZDQRGBGRVRW5LPJWKUNS3M66LZ3KYC/
- https://bugs.launchpad.net/ubuntu/+source/initramfs-tools/+bug/1835096
- https://calamares.io/calamares-3.2.11-is-out/
- https://calamares.io/calamares-cve-2019/
- https://www.pavelkogan.com/2014/05/23/luks-full-disk-encryption/
- https://www.pavelkogan.com/2015/01/25/linux-mint-encryption/
- https://bugs.launchpad.net/ubuntu/+source/initramfs-tools/+bug/1835095
- https://bugzilla.redhat.com/show_bug.cgi?id=1726565
- https://github.com/calamares/calamares/issues/1190
- https://github.com/calamares/calamares/issues/1191
