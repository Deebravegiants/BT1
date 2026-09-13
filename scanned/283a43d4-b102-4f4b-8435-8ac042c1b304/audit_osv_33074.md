# [C] drbd: add missing kref_get in handle_write_conflicts

## Summary
Severity: Critical
Advisory: CVE-2025-38708
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38708
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drbd: add missing kref_get in handle_write_conflicts

With `two-primaries` enabled, DRBD tries to detect "concurrent" writes
and handle write conflicts, so that even if you write to the same sector
simultaneously on both nodes, they end up with the identical data once
the writes are completed.

In handling "superseeded" writes, we forgot a kref_get,
resulting in a premature drbd_destroy_device and use after free,
and further to kernel crashes with symptoms.

Relevance: No one should use DRBD as a random data generator, and apparently
all users of "two-primaries" handle concurrent writes correctly on layer up.
That is cluster file systems use some distributed lock manager,
and live migration in virtualization environments stops writes on one node
before starting writes on the other node.

Which means that other than for "test cases",
this code path is never taken in real life.

FYI, in DRBD 9, things are handled differently nowadays.  We still detect
"write conflicts", but no longer try to be smart about them.
We decided to disconnect hard instead: upper layers must not submit concurrent
writes. If they do, that's their fault.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/00c9c9628b49e368d140cfa61d7df9b8922ec2a8
- https://git.kernel.org/stable/c/0336bfe9c237476bd7c45605a36ca79c2bca62e5
- https://git.kernel.org/stable/c/3a896498f6f577e57bf26aaa93b48c22b6d20c20
- https://git.kernel.org/stable/c/46e3763dcae0ffcf8fcfaff4fc10a90a92ffdd89
- https://git.kernel.org/stable/c/57418de35420cedab035aa1da8a26c0499b7f575
- https://git.kernel.org/stable/c/7d483ad300fc0a06f69b019dda8f74970714baf8
- https://git.kernel.org/stable/c/810cd546a29bfac90ed1328ea01d693d4bd11cb1
- https://git.kernel.org/stable/c/84ef8dd3238330d1795745ece83b19f0295751bf
- https://git.kernel.org/stable/c/9f53b2433ad248cd3342cc345f56f5c7904bd8c4
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38708.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38708
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
