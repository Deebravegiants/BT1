# [M] ALSA: scarlett2: Add clamp() in scarlett2_mixer_ctl_put()

## Summary
Severity: Medium
Advisory: CVE-2023-52674
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52674
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: scarlett2: Add clamp() in scarlett2_mixer_ctl_put()

Ensure the value passed to scarlett2_mixer_ctl_put() is between 0 and
SCARLETT2_MIXER_MAX_VALUE so we don't attempt to access outside
scarlett2_mixer_values[].

## References
- https://git.kernel.org/stable/c/03035872e17897ba89866940bbc9cefca601e572
- https://git.kernel.org/stable/c/04f8f053252b86c7583895c962d66747ecdc61b7
- https://git.kernel.org/stable/c/ad945ea8d47dd4454c271510bea24850119847c2
- https://git.kernel.org/stable/c/d8d8897d65061cbe36bf2909057338303a904810
- https://git.kernel.org/stable/c/e517645ead5ea22c69d2a44694baa23fe1ce7c2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52674.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
