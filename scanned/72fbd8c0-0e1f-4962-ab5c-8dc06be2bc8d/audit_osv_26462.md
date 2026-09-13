# [M] drm/msm/mdp5: Add check for kzalloc

## Summary
Severity: Medium
Advisory: CVE-2023-53239
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/mdp5: Add check for kzalloc

As kzalloc may fail and return NULL pointer,
it should be better to check the return value
in order to avoid the NULL pointer dereference.

Patchwork: https://patchwork.freedesktop.org/patch/514154/

## References
- https://git.kernel.org/stable/c/13fcfcb2a9a4787fe4e49841d728f6f2e9fa6911
- https://git.kernel.org/stable/c/37ff771ed008b9cbffd0eab77985968364694ce3
- https://git.kernel.org/stable/c/3975ea6eaffe26aec634b5c473e51dc76e73af62
- https://git.kernel.org/stable/c/49907c8873826ee771ba0ca1629e809c6479f617
- https://git.kernel.org/stable/c/82943a0730e00c14b03e25a4b2a1a9477ae89d7b
- https://git.kernel.org/stable/c/bc579a2ee8b2e20c152b24b437d094832d8c9c9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53239.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
