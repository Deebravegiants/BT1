# [M] CVE-2021-47511

## Summary
Severity: Medium
Advisory: CVE-2021-47511
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47511
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: oss: Fix negative period/buffer sizes

The period size calculation in OSS layer may receive a negative value
as an error, but the code there assumes only the positive values and
handle them with size_t.  Due to that, a too big value may be passed
to the lower layers.

This patch changes the code to handle with ssize_t and adds the proper
error checks appropriately.

## References
- https://git.kernel.org/stable/c/502e1146873d870f87da3b8f93d6bf2de5f38d0c
- https://git.kernel.org/stable/c/8af815ab052eaf74addbbfb556d63ce2137c0e1b
- https://git.kernel.org/stable/c/9d2479c960875ca1239bcb899f386970c13d9cfe
- https://git.kernel.org/stable/c/be8869d388593e57223ad39297c8e54be632f2f2
- https://git.kernel.org/stable/c/f12c8a7515f641885677960af450082569a87243
- https://git.kernel.org/stable/c/f96c0959c1ee92adc911c10d6ec209af50105049
- https://git.kernel.org/stable/c/00a860678098fcd9fa8db2b5fb9d2ddf4776d4cc
- https://git.kernel.org/stable/c/02b2b691b77cd7b951fa7b6c9d44d4e472cdc823
