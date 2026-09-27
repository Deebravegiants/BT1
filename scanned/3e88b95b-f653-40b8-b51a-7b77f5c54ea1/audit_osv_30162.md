# [H] tracing: Consider the NULL character when validating the event length

## Summary
Severity: High
Advisory: CVE-2024-50131
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50131
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Consider the NULL character when validating the event length

strlen() returns a string length excluding the null byte. If the string
length equals to the maximum buffer length, the buffer will have no
space for the NULL terminating character.

This commit checks this condition and returns failure for it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/02874ca52df2ca2423ba6122039315ed61c25972
- https://git.kernel.org/stable/c/0b6e2e22cb23105fcb171ab92f0f7516c69c8471
- https://git.kernel.org/stable/c/5e3231b352725ff4a3a0095e6035af674f2d8725
- https://git.kernel.org/stable/c/5fd942598ddeed9a212d1ff41f9f5b47bcc990a7
- https://git.kernel.org/stable/c/a14a075a14af8d622c576145455702591bdde09d
- https://git.kernel.org/stable/c/b86b0d6eea204116e4185acc35041ca4ff11a642
- https://git.kernel.org/stable/c/f4ed40d1c669bba1a54407d8182acdc405683f29
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50131.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50131
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
