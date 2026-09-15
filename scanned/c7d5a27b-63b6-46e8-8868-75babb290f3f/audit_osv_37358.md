# [H] HID: bpf: prevent buffer overflow in hid_hw_request

## Summary
Severity: High
Advisory: CVE-2026-31401
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31401
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: bpf: prevent buffer overflow in hid_hw_request

right now the returned value is considered to be always valid. However,
when playing with HID-BPF, the return value can be arbitrary big,
because it's the return value of dispatch_hid_bpf_raw_requests(), which
calls the struct_ops and we have no guarantees that the value makes
sense.

## References
- https://git.kernel.org/stable/c/2b658c1c442ec1cd9eec5ead98d68662c40fe645
- https://git.kernel.org/stable/c/73c5b5aea1c443239c8cb4191b4af7a4bd6fd7b1
- https://git.kernel.org/stable/c/d6efaa50af62fb0790dd1fd4e7e5506b46312510
- https://git.kernel.org/stable/c/eb57dae20fdf6f3069cdc07821fa3bb46de381d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31401.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31401
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
