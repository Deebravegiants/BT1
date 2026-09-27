# [H] wifi: wilc1000: validate assoc response length before subtracting header

## Summary
Severity: High
Advisory: CVE-2026-68196
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68196
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: validate assoc response length before subtracting header

wilc_parse_assoc_resp_info() computes the trailing IE length as

	ies_len = buffer_len - sizeof(*res);

without first checking that buffer_len is at least sizeof(struct
wilc_assoc_resp) (6 bytes). buffer_len is the length reported for a
received association response (host_int_parse_assoc_resp_info() passes
hif_drv->assoc_resp / assoc_resp_info_len straight in) and must be
validated before the driver accesses the fixed header.

For a frame shorter than the 6-byte fixed header, the subtraction wraps.
For a four-byte response the result is truncated to a u16 ies_len of
65534, so kmemdup() then attempts to copy 65534 bytes starting at
buffer + sizeof(*res), beyond the valid association-response data
(CWE-125). A response shorter than four bytes can also cause an
out-of-bounds read of res->status_code at offsets 2 and 3.

Reject frames too short to hold the fixed header before touching the
header or computing ies_len. Also set the connection status to a failure
on this path: the caller falls through to a
"conn_info->status == WLAN_STATUS_SUCCESS" check after the parser
returns, so leaving the status untouched could let a malformed short
response be treated as a successful association.

## References
- https://git.kernel.org/stable/c/4c4c97b60a5e978121d9ee8cb0ab3916e5d6a8de
- https://git.kernel.org/stable/c/4d410320e8ae5933e651660c9fadc1d380309e23
- https://git.kernel.org/stable/c/584c8954ad55f8b09b475be6db710fe40ceb988c
- https://git.kernel.org/stable/c/8ccdf8c8de87a9580df37c3c1ec53ba88cedef65
- https://git.kernel.org/stable/c/8d50acf5420de0c4da99c2d634731c9d3164a755
- https://git.kernel.org/stable/c/b81d0ea9e1daa215b3da68c1f4f6fb07940c2f6a
- https://git.kernel.org/stable/c/d79b92417f33424ff23dad76716ed8f2cefb1083
- https://git.kernel.org/stable/c/e511e93abd6eeedcd5b3c55516241f414fbde64a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68196.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68196
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
