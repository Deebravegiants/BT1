# [C] scsi: libiscsi_tcp: Bound SCSI Response data segment to the connection buffer

## Summary
Severity: Critical
Advisory: CVE-2026-74556
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74556
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: libiscsi_tcp: Bound SCSI Response data segment to the connection buffer

iscsi_tcp_hdr_dissect() receives the data segment of several PDU types
into the fixed-size conn->data buffer, which is allocated for
ISCSI_DEF_MAX_RECV_SEG_LEN (8192) bytes.  For the LOGIN_RSP, TEXT_RSP,
REJECT and ASYNC_EVENT opcodes the dissect path already rejects a PDU
whose DataSegmentLength exceeds that buffer.

The SCSI Command Response (ISCSI_OP_SCSI_CMD_RSP) path also copies its
data segment (sense/response data) into conn->data via
iscsi_tcp_data_recv_prep(), but it does so without the same check.  The
only upstream bound on in.datalen is conn->max_recv_dlength, the
initiator's advertised MaxRecvDataSegmentLength, which is commonly
negotiated well above 8192 (open-iscsi defaults to 262144).  A target
that returns a SCSI Response with a DataSegmentLength between 8193 and
max_recv_dlength therefore overflows the 8192-byte conn->data buffer.

Once the same bound applies, ISCSI_OP_SCSI_CMD_RSP is handled exactly
like those responses: bound the data segment, receive it into conn->data
when present, and otherwise complete the PDU with no data.  Fold the
opcode into that case group rather than duplicating the check.

## References
- https://git.kernel.org/stable/c/084af0253673425ce2ae62e3c7f74f0dd023711b
- https://git.kernel.org/stable/c/72815741715bd41556dac5eeb068bf0f8af06ee7
- https://git.kernel.org/stable/c/a51812842084fd390590ab8dc0431f10c73ddc56
- https://git.kernel.org/stable/c/a8f94cc9f0e5759252551be3a172960c57f21f54
- https://git.kernel.org/stable/c/b0aa3e8e2ab4ca92adb28a3ef41873b3363b8676
- https://git.kernel.org/stable/c/c1dea15f819cded9b3faf58f8bec72323568b6e6
- https://git.kernel.org/stable/c/c97b5265cc47775f77fd2a23d6bde0426997b233
- https://git.kernel.org/stable/c/f1a3a51fc5dba0e99532379665069f1700da6b44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74556.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74556
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
