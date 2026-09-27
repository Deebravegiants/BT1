# [H] CVE-2019-13179

## Summary
Severity: High
Advisory: CVE-2019-13179
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-02
Source: https://osv.dev/vulnerability/CVE-2019-13179
Type: osv

## Details
Calamares versions 3.1 through 3.2.10 copies a LUKS encryption keyfile from /crypto_keyfile.bin (mode 0600 owned by root) to /boot within a globally readable initramfs image with insecure permissions, which allows this originally protected file to be read by any user, thereby disclosing decryption keys for LUKS containers created with Full Disk Encryption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q57BOTBA2J5U4GVKUP7N2PD5H7B3BVUU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R2ZDQRGBGRVRW5LPJWKUNS3M66LZ3KYC/
- https://bugs.launchpad.net/ubuntu/+source/initramfs-tools/+bug/1835096
- https://calamares.io/calamares-3.2.11-is-out/
- https://calamares.io/calamares-cve-2019/
- https://bugs.launchpad.net/ubuntu/+source/initramfs-tools/+bug/1835095
- https://bugzilla.redhat.com/show_bug.cgi?id=1726542
- https://github.com/calamares/calamares/issues/1191
