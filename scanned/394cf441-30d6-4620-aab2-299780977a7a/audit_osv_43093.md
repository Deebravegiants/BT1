# [H] xfrm: validate selector family and prefixlen during match

## Summary
Severity: High
Advisory: CVE-2026-72450
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72450
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.12.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: validate selector family and prefixlen during match

syzbot reported a shift-out-of-bounds in xfrm_selector_match()
due to AF_UNSPEC selector with large prefixlen (e.g. 128) matched
against IPv4 flow (when XFRM_STATE_AF_UNSPEC is set).

Fix this by:

- Rejecting mismatched families in xfrm_selector_match.
- Returning false in addr4_match if prefixlen > 32.
- Returning false in addr_match if prefixlen > 128 (prevents overflow).

## References
- https://git.kernel.org/stable/c/40f0b1047918539f0b0f795ac65e35336b4c2c78
- https://git.kernel.org/stable/c/5a03a2ee17e8259dde631ed84fd8322db06cb2ae
- https://git.kernel.org/stable/c/6d99379c58f7f1c6ab2cc7aba01a4f52d71adcfe
- https://git.kernel.org/stable/c/78783fefdc8f36879b1a17efa0d3195ea5f2dc5f
- https://git.kernel.org/stable/c/87a5bbccc7ff4edb3f42fea387124237d2ba91ee
- https://git.kernel.org/stable/c/a3968ad4195d72c8fddcc6c0ef39da95ac98711a
- https://git.kernel.org/stable/c/bd7f202cf77556cff59f68dc30e4cdf40cb6e33b
- https://git.kernel.org/stable/c/efa9e3b9f3dea2e1ea4c7edf4edc863faef85986
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72450
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
