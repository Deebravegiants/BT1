# [H] CVE-2021-38202

## Summary
Severity: High
Advisory: CVE-2021-38202
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38202
Type: osv

## Details
fs/nfsd/trace.h in the Linux kernel before 5.13.4 might allow remote attackers to cause a denial of service (out-of-bounds read in strlen) by sending NFS traffic when the trace event framework is being used for nfsd.

## References
- https://security.netapp.com/advisory/ntap-20210902-0010/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.4
- https://github.com/torvalds/linux/commit/7b08cf62b1239a4322427d677ea9363f0ab677c6
