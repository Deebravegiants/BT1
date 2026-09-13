# [M] CVE-2021-29155

## Summary
Severity: Medium
Advisory: CVE-2021-29155
Aliases: A-186337918, PUB-A-186337918
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-20
Source: https://osv.dev/vulnerability/CVE-2021-29155
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.x. kernel/bpf/verifier.c performs undesirable out-of-bounds speculation on pointer arithmetic, leading to side-channel attacks that defeat Spectre mitigations and obtain sensitive information from kernel memory. Specifically, for sequences of pointer arithmetic operations, the pointer modification performed by the first operation is not correctly accounted for when restricting subsequent operations.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=073815b756c51ba9d8384d924c5d1c03ca3d1ae4
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=24c109bb1537c12c02aeed2d51a347b4d6a9b76e
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6f55b2f2a1178856c19bbce2f71449926e731914
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7fedb63a8307dda0ec3b8969a3b233a1dd7ea8e0
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9601148392520e2e134936e76788fc2a6371e7be
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b658bbb844e28f1862867f37e8ca11a8e2aa94a3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAEQ3H6HKNO6KUCGRZVYSFSAGEUX23JL/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a6aaece00a57fa6f22575364b3903dfbccf5345d
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f528819334881fd622fdadeddb3f7edaed8b7c9b
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CUX2CA63453G34C6KYVBLJXJXEARZI2X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XZASHZVCOFJ4VU2I3BN5W5EPHWJQ7QWX/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://www.kernel.org
- https://www.openwall.com/lists/oss-security/2021/04/18/4
