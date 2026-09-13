# [M] of: module: prevent NULL pointer dereference in vsnprintf()

## Summary
Severity: Medium
Advisory: CVE-2024-35878
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35878
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

of: module: prevent NULL pointer dereference in vsnprintf()

In of_modalias(), we can get passed the str and len parameters which would
cause a kernel oops in vsnprintf() since it only allows passing a NULL ptr
when the length is also 0. Also, we need to filter out the negative values
of the len parameter as these will result in a really huge buffer since
snprintf() takes size_t parameter while ours is ssize_t...

Found by Linux Verification Center (linuxtesting.org) with the Svace static
analysis tool.

## References
- https://git.kernel.org/stable/c/544561dc56f7e69a053c25e11e6170f48bb97898
- https://git.kernel.org/stable/c/a1aa5390cc912934fee76ce80af5f940452fa987
- https://git.kernel.org/stable/c/e4a449368a2ce6d57a775d0ead27fc07f5a86e5b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35878.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35878
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
