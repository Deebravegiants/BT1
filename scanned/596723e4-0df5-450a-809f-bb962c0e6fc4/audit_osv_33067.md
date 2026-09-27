# [H] media: venus: Fix OOB read due to missing payload bound check

## Summary
Severity: High
Advisory: CVE-2025-38679
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38679
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: Fix OOB read due to missing payload bound check

Currently, The event_seq_changed() handler processes a variable number
of properties sent by the firmware. The number of properties is indicated
by the firmware and used to iterate over the payload. However, the
payload size is not being validated against the actual message length.

This can lead to out-of-bounds memory access if the firmware provides a
property count that exceeds the data available in the payload. Such a
condition can result in kernel crashes or potential information leaks if
memory beyond the buffer is accessed.

Fix this by properly validating the remaining size of the payload before
each property access and updating bounds accordingly as properties are
parsed.

This ensures that property parsing is safely bounded within the received
message buffer and protects against malformed or malicious firmware
behavior.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/06d6770ff0d8cc8dfd392329a8cc03e2a83e7289
- https://git.kernel.org/stable/c/6f08bfb5805637419902f3d70069fe17a404545b
- https://git.kernel.org/stable/c/8f274e2b05fdae7a53cee83979202b5ecb49035c
- https://git.kernel.org/stable/c/a3eef5847603cd8a4110587907988c3f93c9605a
- https://git.kernel.org/stable/c/bed4921055dd7bb4d2eea2729852ae18cf97a2c6
- https://git.kernel.org/stable/c/c956c3758510b448b3d4d10d1da8230e8c9bf668
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38679.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38679
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
