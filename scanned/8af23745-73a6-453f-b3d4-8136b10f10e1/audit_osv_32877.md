# [H] ksmbd: fix null pointer dereference in destroy_previous_session

## Summary
Severity: High
Advisory: CVE-2025-38191
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38191
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix null pointer dereference in destroy_previous_session

If client set ->PreviousSessionId on kerberos session setup stage,
NULL pointer dereference error will happen. Since sess->user is not
set yet, It can pass the user argument as NULL to destroy_previous_session.
sess->user will be set in ksmbd_krb5_authenticate(). So this patch move
calling destroy_previous_session() after ksmbd_krb5_authenticate().

## References
- https://git.kernel.org/stable/c/076f1adefb9837977af7ed233883842ddc446644
- https://git.kernel.org/stable/c/0902625a24eea7fdc187faa5d97df244d159dd6e
- https://git.kernel.org/stable/c/1193486dffb7432a09f57f5d09049b4d4123538b
- https://git.kernel.org/stable/c/281afc52e2961cd5dd8326ebc9c5bc40904c0468
- https://git.kernel.org/stable/c/7ac5b66acafcc9292fb935d7e03790f2b8b2dc0e
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38191.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38191
- https://www.zerodayinitiative.com/advisories/ZDI-25-610/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
