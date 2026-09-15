# [H] virt: tdx-guest: Fix handling of host controlled 'quote' buffer length

## Summary
Severity: High
Advisory: CVE-2026-31470
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31470
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

virt: tdx-guest: Fix handling of host controlled 'quote' buffer length

Validate host controlled value `quote_buf->out_len` that determines how
many bytes of the quote are copied out to guest userspace. In TDX
environments with remote attestation, quotes are not considered private,
and can be forwarded to an attestation server.

Catch scenarios where the host specifies a response length larger than
the guest's allocation, or otherwise races modifying the response while
the guest consumes it.

This prevents contents beyond the pages allocated for `quote_buf`
(up to TSM_REPORT_OUTBLOB_MAX) from being read out to guest userspace,
and possibly forwarded in attestation requests.

Recall that some deployments want per-container configs-tsm-report
interfaces, so the leak may cross container protection boundaries, not
just local root.

## References
- https://git.kernel.org/stable/c/02ca2d9d197723696cb9cc0cb159eb7e8bf5f89b
- https://git.kernel.org/stable/c/6f3c8795ae9ba74fa10fe979293d1904712d3fb1
- https://git.kernel.org/stable/c/a079a62883e3365de592cea9f7a669d8115433b0
- https://git.kernel.org/stable/c/c3fd16c3b98ed726294feab2f94f876290bf7b61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31470.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31470
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
