# [H] CVE-2015-8312

## Summary
Severity: High
Advisory: CVE-2015-8312
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2015-8312
Type: osv

## Details
Off-by-one error in afs_pioctl.c in OpenAFS before 1.6.16 might allow local users to cause a denial of service (memory overwrite and system crash) via a pioctl with an input buffer size of 4096 bytes.

## References
- http://www.debian.org/security/2016/dsa-3569
- https://www.openafs.org/dl/1.6.16/RELNOTES-1.6.16
- http://git.openafs.org/?p=openafs.git%3Ba=commitdiff%3Bh=2ef863720da4d9f368aaca0461c672a3008195ca
