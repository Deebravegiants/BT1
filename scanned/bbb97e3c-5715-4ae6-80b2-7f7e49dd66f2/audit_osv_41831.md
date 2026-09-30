# [H] Bluetooth: HIDP: fix missing length checks in hidp_input_report()

## Summary
Severity: High
Advisory: CVE-2026-63947
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63947
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: HIDP: fix missing length checks in hidp_input_report()

hidp_input_report() reads keyboard and mouse payload data from an skb
without first verifying that skb->len contains enough data.

hidp_recv_intr_frame() pulls the 1-byte HIDP header before dispatching
to hidp_input_report(). If a paired device sends a truncated packet,
the handler reads beyond the valid skb data, resulting in an
out-of-bounds read of skb data. The OOB bytes may be interpreted as
phantom key presses or spurious mouse movement.

Replace the open-coded length tracking and pointer arithmetic with
skb_pull_data() calls. skb_pull_data() returns NULL if the requested
bytes are not present, eliminating the need for a manual size variable
and the separate skb->len guard.

## References
- https://git.kernel.org/stable/c/1f08a90013e1e632b34321334e861fcefc056505
- https://git.kernel.org/stable/c/2a3ac9ee11dbb9845f3947cef4a79dba658cf6f6
- https://git.kernel.org/stable/c/6348dfed5b0f9c6074f14322332e97493d32fef0
- https://git.kernel.org/stable/c/b83dcacd2ec7fcc5a48be215f82d573759f87ec2
- https://git.kernel.org/stable/c/cc3832b19f863e3677c5651f001a2e3795f39eb8
- https://git.kernel.org/stable/c/d313683d6ccdd8c01e0562270a2ae25b86d8461d
- https://git.kernel.org/stable/c/d7d6a81b8dd1a8d084a1b755db9406041d53adb5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63947.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
