# [H] sctp: Prevent TOCTOU out-of-bounds write

## Summary
Severity: High
Advisory: CVE-2025-40331
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40331
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: Prevent TOCTOU out-of-bounds write

For the following path not holding the sock lock,

  sctp_diag_dump() -> sctp_for_each_endpoint() -> sctp_ep_dump()

make sure not to exceed bounds in case the address list has grown
between buffer allocation (time-of-check) and write (time-of-use).

## References
- https://git.kernel.org/stable/c/2fe08fcaacb7eb019fa9c81db39b2214de216677
- https://git.kernel.org/stable/c/3006959371007fc2eae4a078f823c680fa52de1a
- https://git.kernel.org/stable/c/584307275b2048991b2e8984962189b6cc0a9b85
- https://git.kernel.org/stable/c/72e3fea68eac8d088e44c3dd954e843478e9240e
- https://git.kernel.org/stable/c/89eac1e150dbd42963e13d23828cb8c4e0763196
- https://git.kernel.org/stable/c/95aef86ab231f047bb8085c70666059b58f53c09
- https://git.kernel.org/stable/c/b106a68df0650b694b254427cd9250c04500edd3
- https://git.kernel.org/stable/c/c9119f243d9c0da3c3b5f577a328de3e7ffd1b42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40331.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40331
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
