# [C] sctp: validate embedded address parameter length

## Summary
Severity: Critical
Advisory: CVE-2026-74287
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74287
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate embedded address parameter length

sctp_verify_asconf() and sctp_verify_param() only validate ADD_IP, DEL_IP,
and SET_PRIMARY parameters against a fixed minimum size of sizeof(struct
sctp_addip_param) + sizeof(struct sctp_paramhdr). This ensures the outer
parameter is large enough to contain an embedded address parameter header,
but does not verify that the embedded address parameter's declared length
fits within the bounds of the outer parameter.

Later, sctp_process_param() and sctp_process_asconf_param() extract the
embedded address parameter and pass it to af->from_addr_param(), which uses
the address parameter length to parse the variable-length address payload.
A malformed peer can therefore advertise an embedded address parameter
length that exceeds the remaining bytes in the enclosing parameter.

Validate that addr_param->p.length does not exceed the space available
after the sctp_addip_param header before processing the embedded address
parameter. Reject malformed parameters when the embedded address length
extends beyond the enclosing parameter bounds.

This prevents out-of-bounds reads when parsing malformed parameters carried
in INIT or ASCONF processing paths.

## References
- https://git.kernel.org/stable/c/06c8bf48505f2fef265931db82d5003d302a347b
- https://git.kernel.org/stable/c/0c674b20c9cdb54f8a46c88b4d00cadf82b8f0c0
- https://git.kernel.org/stable/c/28ba1d3c956604a89168adfb4c97cfc6c509bba5
- https://git.kernel.org/stable/c/3a44b2602d57e11e2eb85958d4cd500d14a27d9e
- https://git.kernel.org/stable/c/85f54cf589163a75fa06e37d8c2a4a72824c6dd1
- https://git.kernel.org/stable/c/92e4adfee56f32a963ebb105c6cd9a1ed707262a
- https://git.kernel.org/stable/c/e9361d0ca55c4af12aac09e2572852fa91046229
- https://git.kernel.org/stable/c/ed8605c6f39b9b84f9a4631db6deb25e7f1e973c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74287.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
