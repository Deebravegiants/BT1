# [H] bus: mhi: host: Detect events pointing to unexpected TREs

## Summary
Severity: High
Advisory: CVE-2025-39790
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39790
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: mhi: host: Detect events pointing to unexpected TREs

When a remote device sends a completion event to the host, it contains a
pointer to the consumed TRE. The host uses this pointer to process all of
the TREs between it and the host's local copy of the ring's read pointer.
This works when processing completion for chained transactions, but can
lead to nasty results if the device sends an event for a single-element
transaction with a read pointer that is multiple elements ahead of the
host's read pointer.

For instance, if the host accesses an event ring while the device is
updating it, the pointer inside of the event might still point to an old
TRE. If the host uses the channel's xfer_cb() to directly free the buffer
pointed to by the TRE, the buffer will be double-freed.

This behavior was observed on an ep that used upstream EP stack without
'commit 6f18d174b73d ("bus: mhi: ep: Update read pointer only after buffer
is written")'. Where the device updated the events ring pointer before
updating the event contents, so it left a window where the host was able to
access the stale data the event pointed to, before the device had the
chance to update them. The usual pattern was that the host received an
event pointing to a TRE that is not immediately after the last processed
one, so it got treated as if it was a chained transaction, processing all
of the TREs in between the two read pointers.

This commit aims to harden the host by ensuring transactions where the
event points to a TRE that isn't local_rp + 1 are chained.

[mani: added stable tag and reworded commit message]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/2ec99b922f4661521927eeada76f431eebfbabc4
- https://git.kernel.org/stable/c/4079c6c59705b96285219b9efc63cab870d757b7
- https://git.kernel.org/stable/c/44e1a079e18f78d6594a715b0c6d7e18c656f7b9
- https://git.kernel.org/stable/c/5bd398e20f0833ae8a1267d4f343591a2dd20185
- https://git.kernel.org/stable/c/5e17429679a8545afe438ce7a82a13a54e8ceabb
- https://git.kernel.org/stable/c/7b3f0e3b60c27f4fcb69927d84987e5fd6240530
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39790.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39790
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
