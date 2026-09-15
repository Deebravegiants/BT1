# [C] tls: fix race between async notify and socket close

## Summary
Severity: Critical
Advisory: CVE-2024-26583
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-26583
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.15.160, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: fix race between async notify and socket close

The submitting thread (one which called recvmsg/sendmsg)
may exit as soon as the async crypto handler calls complete()
so any code past that point risks touching already freed data.

Try to avoid the locking and extra flags altogether.
Have the main thread hold an extra reference, this way
we can depend solely on the atomic ref counter for
synchronization.

Don't futz with reiniting the completion, either, we are now
tightly controlling when completion fires.

## References
- https://git.kernel.org/stable/c/6209319b2efdd8524691187ee99c40637558fa33
- https://git.kernel.org/stable/c/7a3ca06d04d589deec81f56229a9a9d62352ce01
- https://git.kernel.org/stable/c/86dc27ee36f558fe223dbdfbfcb6856247356f4a
- https://git.kernel.org/stable/c/aec7961916f3f9e88766e2688992da6980f11b8d
- https://git.kernel.org/stable/c/f17d21ea73918ace8afb9c2d8e734dbf71c2c9d7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26583.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26583
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
