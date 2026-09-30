# [C] ceph: fix potential use-after-free bug when trimming caps

## Summary
Severity: Critical
Advisory: CVE-2023-53867
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-53867
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix potential use-after-free bug when trimming caps

When trimming the caps and just after the 'session->s_cap_lock' is
released in ceph_iterate_session_caps() the cap maybe removed by
another thread, and when using the stale cap memory in the callbacks
it will trigger use-after-free crash.

We need to check the existence of the cap just after the 'ci->i_ceph_lock'
being acquired. And do nothing if it's already removed.

## References
- https://git.kernel.org/stable/c/2b2515b8095cf2149bef44383a99d5b5677f1831
- https://git.kernel.org/stable/c/448875a73e16ba7d81dec9274ce9d33a12d092fb
- https://git.kernel.org/stable/c/aaf67de78807c59c35bafb5003d4fb457c764800
- https://git.kernel.org/stable/c/ae6e935618d99cdba11eab4714092e7e5f13cf7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53867.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
