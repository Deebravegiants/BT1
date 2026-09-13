# [H] crypto: xts - Handle EBUSY correctly

## Summary
Severity: High
Advisory: CVE-2023-53494
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53494
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: xts - Handle EBUSY correctly

As it is xts only handles the special return value of EINPROGRESS,
which means that in all other cases it will free data related to the
request.

However, as the caller of xts may specify MAY_BACKLOG, we also need
to expect EBUSY and treat it in the same way.  Otherwise backlogged
requests will trigger a use-after-free.

## References
- https://git.kernel.org/stable/c/51c082514c2dedf2711c99d93c196cc4eedceb40
- https://git.kernel.org/stable/c/57c3e1d63b63dc0841d41df729297cd7c1c35808
- https://git.kernel.org/stable/c/912eb10b65646ffd222256c78a1c566a3dac177d
- https://git.kernel.org/stable/c/92a07ba4f0af2cccdc2aa5ee32679c9c9714db90
- https://git.kernel.org/stable/c/d5870848879291700fe6c5257dcb48aadd10425c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53494.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53494
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
