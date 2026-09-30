# [C] tls: fix race between tx work scheduling and socket close

## Summary
Severity: Critical
Advisory: CVE-2024-26585
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-26585
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.15.165, >=5.16.0 <6.1.84, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: fix race between tx work scheduling and socket close

Similarly to previous commit, the submitting thread (recvmsg/sendmsg)
may exit as soon as the async crypto handler calls complete().
Reorder scheduling the work before calling complete().
This seems more logical in the first place, as it's
the inverse order of what the submitting thread will do.

## References
- https://git.kernel.org/stable/c/196f198ca6fce04ba6ce262f5a0e4d567d7d219d
- https://git.kernel.org/stable/c/6db22d6c7a6dc914b12c0469b94eb639b6a8a146
- https://git.kernel.org/stable/c/dd32621f19243f89ce830919496a5dcc2158aa33
- https://git.kernel.org/stable/c/e01e3934a1b2d122919f73bc6ddbe1cdafc4bbdb
- https://git.kernel.org/stable/c/e327ed60bff4a991cd7a709c47c4f0c5b4a4fd57
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26585.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26585
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
