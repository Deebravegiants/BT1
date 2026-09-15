# [H] debugfs: fix wait/cancellation handling during remove

## Summary
Severity: High
Advisory: CVE-2024-35793
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35793
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

debugfs: fix wait/cancellation handling during remove

Ben Greear further reports deadlocks during concurrent debugfs
remove while files are being accessed, even though the code in
question now uses debugfs cancellations. Turns out that despite
all the review on the locking, we missed completely that the
logic is wrong: if the refcount hits zero we can finish (and
need not wait for the completion), but if it doesn't we have
to trigger all the cancellations. As written, we can _never_
get into the loop triggering the cancellations. Fix this, and
explain it better while at it.

## References
- https://git.kernel.org/stable/c/3d08cca5fd0aabb62b7015067ab40913b33da906
- https://git.kernel.org/stable/c/952c3fce297f12c7ff59380adb66b564e2bc9b64
- https://git.kernel.org/stable/c/e88b5ae01901c4a655a53158397746334778a57b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35793.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35793
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
