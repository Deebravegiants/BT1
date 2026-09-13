# [H] scsi: lpfc: Revise lpfc_prep_embed_io routine with proper endian macro usages

## Summary
Severity: High
Advisory: CVE-2024-43816
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43816
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Revise lpfc_prep_embed_io routine with proper endian macro usages

On big endian architectures, it is possible to run into a memory out of
bounds pointer dereference when FCP targets are zoned.

In lpfc_prep_embed_io, the memcpy(ptr, fcp_cmnd, sgl->sge_len) is
referencing a little endian formatted sgl->sge_len value.  So, the memcpy
can cause big endian systems to crash.

Redefine the *sgl ptr as a struct sli4_sge_le to make it clear that we are
referring to a little endian formatted data structure.  And, update the
routine with proper le32_to_cpu macro usages.

## References
- https://git.kernel.org/stable/c/8bc7c617642db6d8d20ee671fb6c4513017e7a7e
- https://git.kernel.org/stable/c/9fd003f344d502f65252963169df3dd237054e49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43816.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43816
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
