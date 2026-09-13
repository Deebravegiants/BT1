# [H] CVE-2023-45896

## Summary
Severity: High
Advisory: CVE-2023-45896
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-08-28
Source: https://osv.dev/vulnerability/CVE-2023-45896
Type: osv

## Details
ntfs3 in the Linux kernel through 6.8.0 allows a physically proximate attacker to read kernel memory by mounting a filesystem (e.g., if a Linux distribution is configured to allow unprivileged mounts of removable media) and then leveraging local access to trigger an out-of-bounds read. A length value can be larger than the amount of memory allocated. NOTE: the supplier's perspective is that there is no vulnerability when an attack requires an attacker-modified filesystem image.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.11
- https://dfir.ru/2024/06/19/vulnerabilities-in-7-zip-and-ntfs3/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=013ff63b649475f0ee134e2c8d0c8e65284ede50
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/torvalds/linux/commit/013ff63b649475f0ee134e2c8d0c8e65284ede50
