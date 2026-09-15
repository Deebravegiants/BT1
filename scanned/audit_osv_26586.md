# [H] crypto: seqiv - Handle EBUSY correctly

## Summary
Severity: High
Advisory: CVE-2023-53373
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53373
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: seqiv - Handle EBUSY correctly

As it is seqiv only handles the special return value of EINPROGERSS,
which means that in all other cases it will free data related to the
request.

However, as the caller of seqiv may specify MAY_BACKLOG, we also need
to expect EBUSY and treat it in the same way.  Otherwise backlogged
requests will trigger a use-after-free.

## References
- https://git.kernel.org/stable/c/1effbddaff60eeef8017c6dea1ee0ed970164d14
- https://git.kernel.org/stable/c/32e62025e5e52fbe4812ef044759de7010b15dbc
- https://git.kernel.org/stable/c/36ec108b7bd7e280edb22de028467bd09d644620
- https://git.kernel.org/stable/c/4d497e8b200a175094e0ac252ed878add39b8771
- https://git.kernel.org/stable/c/63551e4b7cbcd9914258827699eb2cb6ed6e4a16
- https://git.kernel.org/stable/c/9477db935eb690f697d9bcc4f608927841bc8b36
- https://git.kernel.org/stable/c/ae849d2f48019ff9c104e32bf588ccbfb200e971
- https://git.kernel.org/stable/c/cc4d0d4251748a8a68026938f4055d2ac47c5719
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53373.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53373
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
