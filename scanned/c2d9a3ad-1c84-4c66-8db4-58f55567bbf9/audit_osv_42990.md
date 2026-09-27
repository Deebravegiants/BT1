# [H] KVM: SEV: Do not allow intra-host migration/mirroring of SNP VMs

## Summary
Severity: High
Advisory: CVE-2026-72286
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72286
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SEV: Do not allow intra-host migration/mirroring of SNP VMs

The intra-host migration/mirroring feature is not fully implemented for
SEV-SNP VMs. The proper migration requires additional SNP-specific
state such as guest_req_mutex, guest_req_buf, and guest_resp_buf to be
transferred or initialized on the destination.

The SNP VM mirroring requires vmsa features to be copied as well otherwise
ASID would be bound to SNP range while VM is detected as a SEV VM.

Reject SNP source VMs in migration/mirroring until proper SNP state
transfer is implemented.


[sean: let lines poke past 80 chars, tag for stable]

## References
- https://git.kernel.org/stable/c/6ee4140788234a6fabf59e6a50e38cdb936008cd
- https://git.kernel.org/stable/c/b70404b89daad5f9f33f7ac640b1065cba639935
- https://git.kernel.org/stable/c/ba06690b28be950bd46d938d9b919c4024292627
- https://git.kernel.org/stable/c/d2f9df3b615ca0cd45899c090366945528186052
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72286.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
