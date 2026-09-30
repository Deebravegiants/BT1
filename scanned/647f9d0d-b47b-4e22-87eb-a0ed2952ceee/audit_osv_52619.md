# [M] CVE-2021-47649

## Summary
Severity: Medium
Advisory: CVE-2021-47649
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47649
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

udmabuf: validate ubuf->pagecount

Syzbot has reported GPF in sg_alloc_append_table_from_pages(). The
problem was in ubuf->pages == ZERO_PTR.

ubuf->pagecount is calculated from arguments passed from user-space. If
user creates udmabuf with list.size == 0 then ubuf->pagecount will be
also equal to zero; it causes kmalloc_array() to return ZERO_PTR.

Fix it by validating ubuf->pagecount before passing it to
kmalloc_array().

## References
- https://git.kernel.org/stable/c/9e9b4a269f84d3230f2af84ff42322db676440d9
- https://git.kernel.org/stable/c/a3728d32fc61eb0fe283cb8ff60b2c8f751e2202
- https://git.kernel.org/stable/c/b267a8118c2b171bf7d67b90ed64154eeab9fae0
- https://git.kernel.org/stable/c/2b6dd600dd72573c23ea180b5b0b2f1813405882
- https://git.kernel.org/stable/c/5d50f851dd307c07ca5591297093f19967c834a9
- https://git.kernel.org/stable/c/811b667cefbea9cb7511a874b169d6a92907137e
