# [M] CVE-2021-47509

## Summary
Severity: Medium
Advisory: CVE-2021-47509
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47509
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: oss: Limit the period size to 16MB

Set the practical limit to the period size (the fragment shift in OSS)
instead of a full 31bit; a too large value could lead to the exhaust
of memory as we allocate temporary buffers of the period size, too.

As of this patch, we set to 16MB limit, which should cover all use
cases.

## References
- https://git.kernel.org/stable/c/be55f306396cd62c6889286a7194fd8b53363aeb
- https://git.kernel.org/stable/c/d1bb703ad050de9095f10b2d3416c32921ac6bcc
- https://git.kernel.org/stable/c/2e54cf6794bf82a54aaefc78da13819aea9cd28a
- https://git.kernel.org/stable/c/35a3e511032146941085f87dd9fb5b82ea5c00a2
- https://git.kernel.org/stable/c/76f19e4cbb548e28547f8c328aa0bfb3a10222d3
- https://git.kernel.org/stable/c/8839c8c0f77ab8fc0463f4ab8b37fca3f70677c2
- https://git.kernel.org/stable/c/ad45babf7886e7a212ee1d5eda9ef49f696db43c
- https://git.kernel.org/stable/c/b02a41eebcc36d4f07196780f2e165ca2c499257
