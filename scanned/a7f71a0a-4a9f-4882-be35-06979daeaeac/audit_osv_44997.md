# [M] libslirp TCP URG OOB Read Information Leak

## Summary
Severity: Medium
Advisory: CVE-2026-9539
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-9539
Type: osv

## Details
An out-of-bounds heap read and integer underflow in the TCP urgent data handling (sosendoob) in freedesktop.org libslirp version before v4.9.2 on hypervisor host environments (e.g., QEMU) allows a privileged guest VM attacker (root or CAP_NET_RAW) to leak gigabytes of sensitive host-process heap memory via sending crafted TCP segments with manipulated URG flags and urgent pointers (ti_urp).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9539.json
- https://gitlab.freedesktop.org/slirp/libslirp/-/releases/v4.9.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-9539
- https://gitlab.freedesktop.org/slirp/libslirp/-/work_items/93
- https://gitlab.freedesktop.org/slirp/libslirp/-/commit/927bca7344e31fd58e2f7afaca784aad4400eb84
- https://gitlab.freedesktop.org/slirp/libslirp/
