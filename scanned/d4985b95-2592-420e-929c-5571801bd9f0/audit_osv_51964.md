# [M] CVE-2021-46904

## Summary
Severity: Medium
Advisory: CVE-2021-46904
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2021-46904
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hso: fix null-ptr-deref during tty device unregistration

Multiple ttys try to claim the same the minor number causing a double
unregistration of the same device. The first unregistration succeeds
but the next one results in a null-ptr-deref.

The get_free_serial_index() function returns an available minor number
but doesn't assign it immediately. The assignment is done by the caller
later. But before this assignment, calls to get_free_serial_index()
would return the same minor number.

Fix this by modifying get_free_serial_index to assign the minor number
immediately after one is found to be and rename it to obtain_minor()
to better reflect what it does. Similary, rename set_serial_by_index()
to release_minor() and modify it to free up the minor number of the
given hso_serial. Every obtain_minor() should have corresponding
release_minor() call.

## References
- https://git.kernel.org/stable/c/caf5ac93b3b5d5fac032fc11fbea680e115421b4
- https://git.kernel.org/stable/c/dc195928d7e4ec7b5cfc6cd10dc4c8d87a7c72ac
- https://git.kernel.org/stable/c/145c89c441d27696961752bf51b323f347601bee
- https://git.kernel.org/stable/c/388d05f70f1ee0cac4a2068fd295072f1a44152a
- https://git.kernel.org/stable/c/4a2933c88399c0ebc738db39bbce3ae89786d723
- https://git.kernel.org/stable/c/8a12f8836145ffe37e9c8733dce18c22fb668b66
- https://git.kernel.org/stable/c/92028d7a31e55d53e41cff679156b9432cffcb36
- https://git.kernel.org/stable/c/a462067d7c8e6953a733bf5ade8db947b1bb5449
