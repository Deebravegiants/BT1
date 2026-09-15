# [H] smb: client: mask server-provided mode to 07777 in modefromsid

## Summary
Severity: High
Advisory: CVE-2026-64379
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64379
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: mask server-provided mode to 07777 in modefromsid

When modefromsid is active, parse_dacl() applies the server-provided
sub_auth[2] value from the NFS mode SID to cf_mode without masking to
07777. Apply the correct masking, same as in the read path.

## References
- https://git.kernel.org/stable/c/08c600b7e1818539ba5efee4cdb06215c245ca78
- https://git.kernel.org/stable/c/5f6f2241034f189c69d4d0b5f8fe24a0c25b0c14
- https://git.kernel.org/stable/c/b84e002e0df26bbc6cbd3ca01b8212601fe0ae7d
- https://git.kernel.org/stable/c/c6c484a7d5bff6b929a86d7ed5130f29834c6a0d
- https://git.kernel.org/stable/c/e3d9c7160d483fc8f9e225aafad8ecbbc43f3151
- https://git.kernel.org/stable/c/ee2216dbdf0c677e89bb43e03247dba590ed00ef
- https://git.kernel.org/stable/c/f511807feee7cb29b61bdfa86472c7e9e2e5df94
- https://git.kernel.org/stable/c/f80add1bfb3425100a325b14f19648e75669a954
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64379.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64379
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
