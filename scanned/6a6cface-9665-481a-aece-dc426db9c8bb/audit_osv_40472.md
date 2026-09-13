# [H] tee: optee: prevent use-after-free when the client exits before the supplicant

## Summary
Severity: High
Advisory: CVE-2026-53273
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53273
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.14.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

tee: optee: prevent use-after-free when the client exits before the supplicant

Commit 70b0d6b0a199 ("tee: optee: Fix supplicant wait loop") made the
client wait as killable so it can be interrupted during shutdown or
after a supplicant crash. This changes the original lifetime expectations:
the client task can now terminate while the supplicant is still processing
its request.

If the client exits first it removes the request from its queue and
kfree()s it, while the request ID remains in supp->idr. A subsequent
lookup on the supplicant path then dereferences freed memory, leading to
a use-after-free.

Serialise access to the request with supp->mutex:

  * Hold supp->mutex in optee_supp_recv() and optee_supp_send() while
    looking up and touching the request.
  * Let optee_supp_thrd_req() notice that the client has terminated and
    signal optee_supp_send() accordingly.

With these changes the request cannot be freed while the supplicant still
has a reference, eliminating the race.

## References
- https://git.kernel.org/stable/c/373152c94e57e9592b68c100e224fbd943cfd608
- https://git.kernel.org/stable/c/387a926ee166814611acecb960207fe2f3c4fd3e
- https://git.kernel.org/stable/c/416259cb5bffecaaae5f76539deb535a8c1b2c34
- https://git.kernel.org/stable/c/724d0caffd4204b46f78efe22f18f8338031c6e1
- https://git.kernel.org/stable/c/9a0dc9279d0907b198f205a693aedf696b08145d
- https://git.kernel.org/stable/c/ae847ab29ded2d7cece4d5970f0edefa4137bf2f
- https://git.kernel.org/stable/c/d366a01475f927402c96a3fe78bfc06b924fc87d
- https://git.kernel.org/stable/c/d5b57bb314d79e99bebb58a53588fa11dd4dbf69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53273.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
