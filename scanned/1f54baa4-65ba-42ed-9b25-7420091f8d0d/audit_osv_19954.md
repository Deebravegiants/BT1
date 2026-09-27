# [H] CVE-2021-28302

## Summary
Severity: High
Advisory: CVE-2021-28302
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-12
Source: https://osv.dev/vulnerability/CVE-2021-28302
Type: osv

## Details
A stack overflow in pupnp before version 1.14.5 can cause the denial of service through the Parser_parseDocument() function. ixmlNode_free() will release a child node recursively, which will consume stack space and lead to a crash.

## References
- https://github.com/pupnp/pupnp/releases/tag/release-1.14.5
- https://github.com/pupnp/pupnp/issues/249
