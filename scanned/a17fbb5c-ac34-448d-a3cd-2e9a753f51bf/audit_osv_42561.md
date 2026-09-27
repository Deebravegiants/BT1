# [C] ksmbd: validate minimum PDU size for transform requests

## Summary
Severity: Critical
Advisory: CVE-2026-68431
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68431
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.4.0 <6.12.105, >=6.7.0 <6.18.46, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate minimum PDU size for transform requests

The receive path applies the minimum SMB2 PDU size check only when
ProtocolId is SMB2_PROTO_NUMBER. A packet carrying
SMB2_TRANSFORM_PROTO_NUM bypasses the check even when the negotiated
dialect does not provide transform handling.

On an SMB 2.1 connection, a short transform packet therefore reaches
init_smb2_rsp_hdr(), which interprets the request as a full SMB2 header
and reads beyond the request allocation. The copied fields can then be
returned to the unauthenticated client.

Compression transforms are converted to ordinary SMB2 messages before
protocol validation. After that conversion, validate ordinary SMB2
requests against SMB2_MIN_SUPPORTED_PDU_SIZE and require encryption
transform requests to contain both a transform header and an SMB2
header. This rejects truncated requests before work allocation.

## References
- https://git.kernel.org/stable/c/22f1aa35b87e471cc31b35b74451f46630863b12
- https://git.kernel.org/stable/c/32e486b70c256d5ef4baa5a2936ade2fea50e8eb
- https://git.kernel.org/stable/c/928dda88d0e13fbca381255028f65b244343a4ea
- https://git.kernel.org/stable/c/b62c510f59803f82f9b4c76ead2a56833b2984c7
- https://git.kernel.org/stable/c/cfc0b8e5080aec87700774e8568765eaa4b7b92b
- https://git.kernel.org/stable/c/d8e5c5672724b8f3c4c099d2cf60239c996e5424
- https://git.kernel.org/stable/c/d9e9753dfd43bd27c956578df7804a3c90b80fdc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68431
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
