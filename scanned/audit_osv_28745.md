# [C] keys: Fix overwrite of key expiration on instantiation

## Summary
Severity: Critical
Advisory: CVE-2024-36031
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36031
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.9.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

keys: Fix overwrite of key expiration on instantiation

The expiry time of a key is unconditionally overwritten during
instantiation, defaulting to turn it permanent. This causes a problem
for DNS resolution as the expiration set by user-space is overwritten to
TIME64_MAX, disabling further DNS updates. Fix this by restoring the
condition that key_set_expiry is only called when the pre-parser sets a
specific expiry.

## References
- https://git.kernel.org/stable/c/25777f3f4e1f371d16a594925f31e37ce07b6ec7
- https://git.kernel.org/stable/c/939a08bcd4334bad4b201e60bd0ae1f278d71d41
- https://git.kernel.org/stable/c/9da27fb65a14c18efd4473e2e82b76b53ba60252
- https://git.kernel.org/stable/c/ad2011ea787928b2accb5134f1e423b11fe80a8a
- https://git.kernel.org/stable/c/cc219cb8afbc40ec100c0de941047bb29373126a
- https://git.kernel.org/stable/c/e4519a016650e952ad9eb27937f8c447d5a4e06d
- https://git.kernel.org/stable/c/ed79b93f725cd0da39a265dc23d77add1527b9be
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36031.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36031
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
