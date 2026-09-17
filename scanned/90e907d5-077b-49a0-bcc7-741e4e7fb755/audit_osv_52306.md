# [M] CVE-2021-47307

## Summary
Severity: Medium
Advisory: CVE-2021-47307
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47307
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: prevent NULL deref in cifs_compose_mount_options()

The optional @ref parameter might contain an NULL node_name, so
prevent dereferencing it in cifs_compose_mount_options().

Addresses-Coverity: 1476408 ("Explicit null dereferenced")

## References
- https://git.kernel.org/stable/c/ae3d181f4e912f51af7776ea165f199b16fc165d
- https://git.kernel.org/stable/c/e58c162789becede894d3e94c0ce6695a2ef5796
- https://git.kernel.org/stable/c/f7d1fa65e74263d11f90ddd33b4d4cd905a93759
- https://git.kernel.org/stable/c/03313d1c3a2f086bb60920607ab79ac8f8578306
