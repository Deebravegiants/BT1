# [M] CVE-2022-1280

## Summary
Severity: Medium
Advisory: CVE-2022-1280
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/CVE-2022-1280
Type: osv

## Details
A use-after-free vulnerability was found in drm_lease_held in drivers/gpu/drm/drm_lease.c in the Linux kernel due to a race problem. This flaw allows a local user privilege attacker to cause a denial of service (DoS) or a kernel information leak.

## References
- https://www.openwall.com/lists/oss-security/2022/04/12/3
- https://bugzilla.redhat.com/show_bug.cgi?id=2071022
