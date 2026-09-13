# [M] drm/amd/display: Disable PSR-SU on Parade 08-01 TCON too

## Summary
Severity: Medium
Advisory: CVE-2024-50108
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50108
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Disable PSR-SU on Parade 08-01 TCON too

Stuart Hayhurst has found that both at bootup and fullscreen VA-API video
is leading to black screens for around 1 second and kernel WARNING [1] traces
when calling dmub_psr_enable() with Parade 08-01 TCON.

These symptoms all go away with PSR-SU disabled for this TCON, so disable
it for now while DMUB traces [2] from the failure can be analyzed and the failure
state properly root caused.

(cherry picked from commit afb634a6823d8d9db23c5fb04f79c5549349628b)

## References
- https://git.kernel.org/stable/c/5660bcc4dd533005248577d5042f1c48cce2b443
- https://git.kernel.org/stable/c/ba1959f71117b27f3099ee789e0815360b4081dd
- https://git.kernel.org/stable/c/c79e0a18e4b301401bb745702830be9041cfbf04
- https://git.kernel.org/stable/c/fc6afa07b5e251148fb37600ee06e1a7007178c3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50108.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
