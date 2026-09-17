# [H] CVE-2021-3715

## Summary
Severity: High
Advisory: CVE-2021-3715
Aliases: A-223966861, PUB-A-223966861
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3715
Type: osv

## Details
A flaw was found in the "Routing decision" classifier in the Linux kernel's Traffic Control networking subsystem in the way it handled changing of classification filters, leading to a use-after-free condition. This flaw allows unprivileged local users to escalate their privileges on the system. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ef299cc3fa1a9e1288665a9fdc8bff55629fd359
