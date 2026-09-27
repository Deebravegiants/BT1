# [H] smb: client: fix OOB reads parsing symlink error response

## Summary
Severity: High
Advisory: CVE-2026-31613
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31613
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix OOB reads parsing symlink error response

When a CREATE returns STATUS_STOPPED_ON_SYMLINK, smb2_check_message()
returns success without any length validation, leaving the symlink
parsers as the only defense against an untrusted server.

symlink_data() walks SMB 3.1.1 error contexts with the loop test "p <
end", but reads p->ErrorId at offset 4 and p->ErrorDataLength at offset
0.  When the server-controlled ErrorDataLength advances p to within 1-7
bytes of end, the next iteration will read past it.  When the matching
context is found, sym->SymLinkErrorTag is read at offset 4 from
p->ErrorContextData with no check that the symlink header itself fits.

smb2_parse_symlink_response() then bounds-checks the substitute name
using SMB2_SYMLINK_STRUCT_SIZE as the offset of PathBuffer from
iov_base.  That value is computed as sizeof(smb2_err_rsp) +
sizeof(smb2_symlink_err_rsp), which is correct only when
ErrorContextCount == 0.

With at least one error context the symlink data sits 8 bytes deeper,
and each skipped non-matching context shifts it further by 8 +
ALIGN(ErrorDataLength, 8).  The check is too short, allowing the
substitute name read to run past iov_len.  The out-of-bound heap bytes
are UTF-16-decoded into the symlink target and returned to userspace via
readlink(2).

Fix this all up by making the loops test require the full context header
to fit, rejecting sym if its header runs past end, and bound the
substitute name against the actual position of sym->PathBuffer rather
than a fixed offset.

Because sub_offs and sub_len are 16bits, the pointer math will not
overflow here with the new greater-than.

## References
- https://git.kernel.org/stable/c/043834e72337ee7b4e9685859888623ba1504ac7
- https://git.kernel.org/stable/c/20ac98f0eb6047edb73c9a27af782bdde08b3757
- https://git.kernel.org/stable/c/3df690bba28edec865cf7190be10708ad0ddd67e
- https://git.kernel.org/stable/c/781902e069f4ecb6c3b83502f181972c1446110a
- https://git.kernel.org/stable/c/a66ef2e7ed837325c5600f8617d5ee0a0a149fdd
- https://git.kernel.org/stable/c/d65a64755a3df68a2fd19d2a81395e9f723aca23
- https://git.kernel.org/stable/c/e0dd90d14cbbf318157ea8e3fb62ee68a28655ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31613.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31613
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
