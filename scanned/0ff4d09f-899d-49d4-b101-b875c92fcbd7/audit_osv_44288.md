# [H] ovpn: ensure socket is owned by ovpn before deref sk_user_data

## Summary
Severity: High
Advisory: CVE-2026-80735
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80735
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: ensure socket is owned by ovpn before deref sk_user_data

Some subsystems, like BPF SOCKMAP, set sk_user_data without
actually setting the encap_type.

For this reason, we must make sure that the type is the
one ovpn expects before dereferencing sk_user_data.

Failing to do so may lead to out-of-bounds reads.

## References
- https://git.kernel.org/stable/c/43a31142e1d22b3cf5490bd94a94db7196901734
- https://git.kernel.org/stable/c/59aed1eb60d70678a53acccb0cb337a26ce6680e
- https://git.kernel.org/stable/c/61fb3cca40ff938671474f4a16adb908c19032d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80735.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
