# [M] s390/dasd: fix double module refcount decrement

## Summary
Severity: Medium
Advisory: CVE-2024-27054
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27054
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.237, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/dasd: fix double module refcount decrement

Once the discipline is associated with the device, deleting the device
takes care of decrementing the module's refcount.  Doing it manually on
this error path causes refcount to artificially decrease on each error
while it should just stay the same.

## References
- https://git.kernel.org/stable/c/9fe0562179d8fa960afca0eaed6d4ba4122a3cc6
- https://git.kernel.org/stable/c/ad999aa18103fa038787b6a8a55020abcf34df1a
- https://git.kernel.org/stable/c/c3116e62ddeff79cae342147753ce596f01fcf06
- https://git.kernel.org/stable/c/ebc5a3bd79e54f98c885c26f0862a27a02c487c5
- https://git.kernel.org/stable/c/ec09bcab32fc4765e0cc97e1b72cdd067135f37e
- https://git.kernel.org/stable/c/edbdb0d94143db46edd373cc93e433832d29fe19
- https://git.kernel.org/stable/c/fa18aa507ea71d8914b6acb2c94db311c757c650
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27054.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27054
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
