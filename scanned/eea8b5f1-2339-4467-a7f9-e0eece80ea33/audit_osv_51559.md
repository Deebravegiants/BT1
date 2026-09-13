# [H] CVE-2021-33200

## Summary
Severity: High
Advisory: CVE-2021-33200
Aliases: A-190011721, PUB-A-190011721
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-33200
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 5.12.7 enforces incorrect limits for pointer arithmetic operations, aka CID-bb01a1bba579. This can be abused to perform out-of-bounds reads and writes in kernel memory, leading to local privilege escalation to root. In particular, there is a corner case where the off reg causes a masking direction change, which then results in an incorrect final aux->alu_limit.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=bb01a1bba579b4b1c5566af24d95f1767859771e
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7LR3OKKPHIBGOMHN476CMLW2T7UG53QX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JJCABL43FT3FKRX5DBPZG25FNKR6CEK4/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3d0220f6861d713213b015b582e9f21e5b28d2e0
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a7036191277f9fa68d92f2071ddc38c09b1e5ee5
- https://security.netapp.com/advisory/ntap-20210706-0004/
- https://www.openwall.com/lists/oss-security/2021/05/27/1
