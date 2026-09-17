# [H] handshake: Require admin permission for DONE command

## Summary
Severity: High
Advisory: CVE-2026-74270
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74270
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

handshake: Require admin permission for DONE command

ACCEPT and DONE are the two downcalls of the handshake genl
family, both intended for use by the trusted handshake agent
(tlshd). ACCEPT already requires GENL_ADMIN_PERM; DONE has
no privilege check at all.

The fd-lookup in handshake_nl_done_doit() only confirms that
some pending handshake request exists for the supplied sockfd;
it does not authenticate the sender. An unprivileged process
that guesses or observes a valid sockfd can therefore submit
a DONE with HANDSHAKE_A_DONE_STATUS == 0, leaving the kernel
consumer to proceed as if the handshake succeeded. A non-zero
status on a forged DONE tears down a legitimate in-flight
handshake before tlshd can report its real result.

## References
- https://git.kernel.org/stable/c/25fb53e43ec006ac69b9e825a7e8a11d63a6083e
- https://git.kernel.org/stable/c/4dafc411948469277b276724c3b2b4408c02c04c
- https://git.kernel.org/stable/c/67cec2f1eb9e58719d622e92e2278ceda72dbd85
- https://git.kernel.org/stable/c/81246a65303d9635266b1334490142caaf86a11f
- https://git.kernel.org/stable/c/b6557f912509abe8e70223373dd7a44d1d4a0d6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
