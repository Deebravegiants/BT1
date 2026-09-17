# [C] ksmbd: validate mech token in session setup

## Summary
Severity: Critical
Advisory: CVE-2024-26594
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2024-26594
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.149, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate mech token in session setup

If client send invalid mech token in session setup request, ksmbd
validate and make the error if it is invalid.

## References
- https://git.kernel.org/stable/c/5e6dfec95833edc54c48605a98365a7325e5541e
- https://git.kernel.org/stable/c/6eb8015492bcc84e40646390e50a862b2c0529c9
- https://git.kernel.org/stable/c/92e470163d96df8db6c4fa0f484e4a229edb903d
- https://git.kernel.org/stable/c/a2b21ef1ea4cf632d19b3a7cc4d4245b8e63202a
- https://git.kernel.org/stable/c/dd1de9268745f0eac83a430db7afc32cbd62e84b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26594.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26594
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
