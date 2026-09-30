# [H] ksmbd: validate EaNameLength in smb2_get_ea()

## Summary
Severity: High
Advisory: CVE-2026-31612
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31612
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate EaNameLength in smb2_get_ea()

smb2_get_ea() reads ea_req->EaNameLength from the client request and
passes it directly to strncmp() as the comparison length without
verifying that the length of the name really is the size of the input
buffer received.

Fix this up by properly checking the size of the name based on the value
received and the overall size of the request, to prevent a later
strncmp() call to use the length as a "trusted" size of the buffer.
Without this check, uninitialized heap values might be slowly leaked to
the client.

## References
- https://git.kernel.org/stable/c/243b206bcb5a7137e8bddd57b2eec81e1ebd3859
- https://git.kernel.org/stable/c/3363a770b193f555f29d76ddf4ced3305c0ccf6d
- https://git.kernel.org/stable/c/4b73376feecb3b61172fe5b4ff42bbbb8531669d
- https://git.kernel.org/stable/c/551dfb15b182abad4600eaf7b37e6eb7000d5b1b
- https://git.kernel.org/stable/c/66751841212c2cc196577453c37f7774ff363f02
- https://git.kernel.org/stable/c/859f11e1bc81a4d32bb3ceeae54bcd296ac675d3
- https://git.kernel.org/stable/c/dfc6878d14acafffbe670bf2576620757a10a3d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31612.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
