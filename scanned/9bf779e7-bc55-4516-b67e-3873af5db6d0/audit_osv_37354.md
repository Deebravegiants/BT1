# [H] Bluetooth: L2CAP: Validate L2CAP_INFO_RSP payload length before access

## Summary
Severity: High
Advisory: CVE-2026-31393
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31393
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Validate L2CAP_INFO_RSP payload length before access

l2cap_information_rsp() checks that cmd_len covers the fixed
l2cap_info_rsp header (type + result, 4 bytes) but then reads
rsp->data without verifying that the payload is present:

 - L2CAP_IT_FEAT_MASK calls get_unaligned_le32(rsp->data), which reads
   4 bytes past the header (needs cmd_len >= 8).

 - L2CAP_IT_FIXED_CHAN reads rsp->data[0], 1 byte past the header
   (needs cmd_len >= 5).

A truncated L2CAP_INFO_RSP with result == L2CAP_IR_SUCCESS triggers an
out-of-bounds read of adjacent skb data.

Guard each data access with the required payload length check.  If the
payload is too short, skip the read and let the state machine complete
with safe defaults (feat_mask and remote_fixed_chan remain zero from
kzalloc), so the info timer cleanup and l2cap_conn_start() still run
and the connection is not stalled.

## References
- https://git.kernel.org/stable/c/187e6fe939295be36063a1d91f8bebee04399a8c
- https://git.kernel.org/stable/c/3b646516cba2ebc4b51a72954903326e7c1e443f
- https://git.kernel.org/stable/c/5229e7d15771eac2b5886bfb1f976aea0c1eec14
- https://git.kernel.org/stable/c/807bd1258453c4c83f6ae9dbc1e7b44860ff40d0
- https://git.kernel.org/stable/c/9aeacde4da0f02d42fd968fd32f245828b230171
- https://git.kernel.org/stable/c/db2872d054e467810078e2b9f440a5b326a601b2
- https://git.kernel.org/stable/c/dd815e6e3918dc75a49aaabac36e4f024d675101
- https://git.kernel.org/stable/c/e7ff754e339e3d5ce29aa9f95352d0186df8fbd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31393.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
