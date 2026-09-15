# [M] CVE-2021-47218

## Summary
Severity: Medium
Advisory: CVE-2021-47218
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47218
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

selinux: fix NULL-pointer dereference when hashtab allocation fails

When the hash table slot array allocation fails in hashtab_init(),
h->size is left initialized with a non-zero value, but the h->htable
pointer is NULL. This may then cause a NULL pointer dereference, since
the policydb code relies on the assumption that even after a failed
hashtab_init(), hashtab_map() and hashtab_destroy() can be safely called
on it. Yet, these detect an empty hashtab only by looking at the size.

Fix this by making sure that hashtab_init() always leaves behind a valid
empty hashtab when the allocation fails.

## References
- https://git.kernel.org/stable/c/dc27f3c5d10c58069672215787a96b4fae01818b
- https://git.kernel.org/stable/c/83c8ab8503adf56bf68dafc7a382f4946c87da79
- https://git.kernel.org/stable/c/b17dd53cac769dd13031b0ca34f90cc65e523fab
