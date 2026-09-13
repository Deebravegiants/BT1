# [M] CVE-2021-47086

## Summary
Severity: Medium
Advisory: CVE-2021-47086
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47086
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

phonet/pep: refuse to enable an unbound pipe

This ioctl() implicitly assumed that the socket was already bound to
a valid local socket name, i.e. Phonet object. If the socket was not
bound, two separate problems would occur:

1) We'd send an pipe enablement request with an invalid source object.
2) Later socket calls could BUG on the socket unexpectedly being
   connected yet not bound to a valid object.

## References
- https://git.kernel.org/stable/c/311601f114859d586d5ef8833d60d3aa23282161
- https://git.kernel.org/stable/c/48c76fc53582e7f13c1e0b11c916e503256c4d0b
- https://git.kernel.org/stable/c/52ad5da8e316fa11e3a50b3f089aa63e4089bf52
- https://git.kernel.org/stable/c/53ccdc73eedaf0e922c45b569b797d2796fbaafa
- https://git.kernel.org/stable/c/75a2f31520095600f650597c0ac41f48b5ba0068
- https://git.kernel.org/stable/c/982b6ba1ce626ef87e5c29f26f2401897554f235
- https://git.kernel.org/stable/c/b10c7d745615a092a50c2e03ce70446d2bec2aca
- https://git.kernel.org/stable/c/0bbdd62ce9d44f3a22059b3d20a0df977d9f6d59
