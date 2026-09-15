# [M] CVE-2023-2430

## Summary
Severity: Medium
Advisory: CVE-2023-2430
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-23
Source: https://osv.dev/vulnerability/CVE-2023-2430
Type: osv

## Details
A vulnerability was found due to missing lock for IOPOLL flaw in io_cqring_event_overflow() in io_uring.c in Linux Kernel. This flaw allows a local attacker with user privilege to trigger a Denial of Service threat.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e12d7a46f65ae4b7d58a5e0c1cbfa825cf8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2430.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2430
- https://www.debian.org/security/2023/dsa-5492
