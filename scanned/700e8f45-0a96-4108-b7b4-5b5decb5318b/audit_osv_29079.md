# [H] xfs: fix log recovery buffer allocation for the legacy h_size fixup

## Summary
Severity: High
Advisory: CVE-2024-39472
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39472
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.165, >=5.16.0 <6.1.105, >=6.2.0 <6.6.46

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: fix log recovery buffer allocation for the legacy h_size fixup

Commit a70f9fe52daa ("xfs: detect and handle invalid iclog size set by
mkfs") added a fixup for incorrect h_size values used for the initial
umount record in old xfsprogs versions.  Later commit 0c771b99d6c9
("xfs: clean up calculation of LR header blocks") cleaned up the log
reover buffer calculation, but stoped using the fixed up h_size value
to size the log recovery buffer, which can lead to an out of bounds
access when the incorrect h_size does not come from the old mkfs
tool, but a fuzzer.

Fix this by open coding xlog_logrec_hblks and taking the fixed h_size
into account for this calculation.

## References
- https://git.kernel.org/stable/c/45cf976008ddef4a9c9a30310c9b4fb2a9a6602a
- https://git.kernel.org/stable/c/57835c0e7152e36b03875dd6c56dfeed685c1b1f
- https://git.kernel.org/stable/c/c2389c074973aa94e34992e7f66dac0de37595b5
- https://git.kernel.org/stable/c/f754591b17d0ee91c2b45fe9509d0cdc420527cb
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39472.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39472
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
