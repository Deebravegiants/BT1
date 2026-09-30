# [H] igb: Do not free q_vector unless new one was allocated

## Summary
Severity: High
Advisory: CVE-2022-50252
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50252
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

igb: Do not free q_vector unless new one was allocated

Avoid potential use-after-free condition under memory pressure. If the
kzalloc() fails, q_vector will be freed but left in the original
adapter->q_vector[v_idx] array position.

## References
- https://git.kernel.org/stable/c/0200f0fbb11e359cc35af72ab10b2ec224e6f633
- https://git.kernel.org/stable/c/0668716506ca66f90d395f36ccdaebc3e0e84801
- https://git.kernel.org/stable/c/314f7092b27749bdde44c14095b5533afa2a3bc8
- https://git.kernel.org/stable/c/3cb18dea11196fb4a06f78294cec5e61985e1aff
- https://git.kernel.org/stable/c/56483aecf6b22eb7dff6315b3a174688c6ad494c
- https://git.kernel.org/stable/c/64ca1969599857143e91aeec4440640656100803
- https://git.kernel.org/stable/c/68e8adbcaf7a8743e473343b38b9dad66e2ac6f3
- https://git.kernel.org/stable/c/6e399577bd397a517df4b938601108c63769ce0a
- https://git.kernel.org/stable/c/f96bd8adc8adde25390965a8c1ee81b73cb62075
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50252.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50252
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
