# [H] IB/mad: Drop unmatched RMPP responses before reassembly

## Summary
Severity: High
Advisory: CVE-2026-68425
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68425
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/mad: Drop unmatched RMPP responses before reassembly

Kernel-handled RMPP receive processing starts reassembly for active
DATA responses before the response is matched to an outstanding send.
The normal match happens later, after ib_process_rmpp_recv_wc() has
either assembled a complete message or consumed the segment.

That ordering lets an unsolicited response that routes to a kernel
RMPP agent by the high TID bits allocate or extend RMPP receive state
before the full TID and source address are checked against a real
request. A reordered burst can therefore reach the receive-side
insertion path even though the response would not match any send.

For kernel-handled RMPP DATA responses, require the existing
ib_find_send_mad() match before entering RMPP reassembly. The matcher
already checks the full TID, management class and source address/GID
against the agent wait, backlog and in-flight send lists. If there is
no match, drop the response without creating RMPP state.

This leaves the RMPP window behavior unchanged and only rejects
responses that have no corresponding request.

## References
- https://git.kernel.org/stable/c/45416c87ebcece1e90f3bc5bc172d106b77c6b69
- https://git.kernel.org/stable/c/6e1bd7f590b0ccfee07f7fe1d48b92059bd37d72
- https://git.kernel.org/stable/c/9634fb1f4d404f36a20ffbcb8797369db69b06bb
- https://git.kernel.org/stable/c/98d2d468b4faa1fdc68c0c6c238389906ee3490c
- https://git.kernel.org/stable/c/ad9c9ad3204f63a46f0f7de29687a8e512f05e29
- https://git.kernel.org/stable/c/bfb9e8243fd2099d1080d09222964d988f991d9b
- https://git.kernel.org/stable/c/d2e52d610b9b09694261632340b801a421e0b0c5
- https://git.kernel.org/stable/c/dfa535c94406c03d3f0c869ef3ba5528e395737c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68425.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
