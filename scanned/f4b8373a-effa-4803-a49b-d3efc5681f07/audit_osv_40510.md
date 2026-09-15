# [H] NFSv4/pNFS: reject zero-length r_addr in nfs4_decode_mp_ds_addr

## Summary
Severity: High
Advisory: CVE-2026-53391
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53391
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4/pNFS: reject zero-length r_addr in nfs4_decode_mp_ds_addr

nfs4_decode_mp_ds_addr() decodes the r_netid and r_addr opaques of a
netaddr4 from a GETDEVICEINFO multipath-DS body, then immediately
calls strrchr(buf, '.') to locate the port separator. Both decodes
use xdr_stream_decode_string_dup(), and the current code checks only
"nlen < 0" / "rlen < 0" before dereferencing the returned string.

When the on-wire opaque has length zero, xdr_stream_decode_opaque_inline()
returns 0 and xdr_stream_decode_string_dup() falls through to its
"*str = NULL; return ret" tail, leaving buf NULL with a return value
of 0. The "< 0" check does not catch this, and the next line is
strrchr(NULL, '.'), a kernel NULL pointer dereference reachable from
any pNFS-flexfile client mounted against a malicious or compromised
metadata server.

Reject the zero-length cases explicitly so the decoder fails with
-EBADMSG (treated as a malformed GETDEVICEINFO body) instead of
panicking the client.

## References
- https://git.kernel.org/stable/c/012d37a568bfbb2c9686f03ade75560bc7139956
- https://git.kernel.org/stable/c/30aae62e50b4e074a90a9a5e15246548fbdc1182
- https://git.kernel.org/stable/c/41fe0f7b84f0cb822ae10ab08592996a592b2a25
- https://git.kernel.org/stable/c/427ab81a811dab4bca9d19f82eec5847ae42646e
- https://git.kernel.org/stable/c/6c344fff2feff9d4d716d8e4ad40e9b5040ee5ea
- https://git.kernel.org/stable/c/76b94cbd32aacf36a641956385a852635c6802b9
- https://git.kernel.org/stable/c/c8e4e0c701d0192a2efb6df059c0f9e19678c23d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
