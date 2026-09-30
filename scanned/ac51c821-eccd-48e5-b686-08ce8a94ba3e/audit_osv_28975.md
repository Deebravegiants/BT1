# [M] drm: bridge: cdns-mhdp8546: Fix possible null pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2024-38548
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38548
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: bridge: cdns-mhdp8546: Fix possible null pointer dereference

In cdns_mhdp_atomic_enable(), the return value of drm_mode_duplicate() is
assigned to mhdp_state->current_mode, and there is a dereference of it in
drm_mode_set_name(), which will lead to a NULL pointer dereference on
failure of drm_mode_duplicate().

Fix this bug add a check of mhdp_state->current_mode.

## References
- https://git.kernel.org/stable/c/32fb2ef124c3301656ac6c789a2ef35ef69a66da
- https://git.kernel.org/stable/c/47889711da20be9b43e1e136e5cb68df37cbcc79
- https://git.kernel.org/stable/c/85d1a27402f81f2e04b0e67d20f749c2a14edbb3
- https://git.kernel.org/stable/c/89788cd9824c28ffcdea40232c458233353d1896
- https://git.kernel.org/stable/c/935a92a1c400285545198ca2800a4c6c519c650a
- https://git.kernel.org/stable/c/ca53b7efd4ba6ae92fd2b3085cb099c745e96965
- https://git.kernel.org/stable/c/dcf53e6103b26e7458be71491d0641f49fbd5840
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38548.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
