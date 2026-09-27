# [M] ALSA: pcm: Check for null pointer of pointer substream before dereferencing it

## Summary
Severity: Medium
Advisory: CVE-2022-49498
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49498
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: Check for null pointer of pointer substream before dereferencing it

Pointer substream is being dereferenced on the assignment of pointer card
before substream is being null checked with the macro PCM_RUNTIME_CHECK.
Although PCM_RUNTIME_CHECK calls BUG_ON, it still is useful to perform the
the pointer check before card is assigned.

## References
- https://git.kernel.org/stable/c/011b559be832194f992f73d6c0d5485f5925a10b
- https://git.kernel.org/stable/c/1f2e28857be1e5c7db39bbc221332215fc5467e3
- https://git.kernel.org/stable/c/7784d22f81a29df2ec57ca90d54f93a35cbcd1a2
- https://git.kernel.org/stable/c/b2421a196cb0911ea95aec1050a0b830464c8fa6
- https://git.kernel.org/stable/c/b41ef7ad9238c22aa2e142f5ce4ce1a1a0d48123
- https://git.kernel.org/stable/c/f2c68c52898f623fe84518da4606538d193b0cca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49498.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49498
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
