# [H] CVE-2023-0030

## Summary
Severity: High
Advisory: CVE-2023-0030
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-08
Source: https://osv.dev/vulnerability/CVE-2023-0030
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s nouveau driver in how a user triggers a memory overflow that causes the nvkm_vma_tail function to fail. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0030.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0030
- https://security.netapp.com/advisory/ntap-20230413-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=2157270
- https://github.com/torvalds/linux/commit/729eba3355674f2d9524629b73683ba1d1cd3f10
