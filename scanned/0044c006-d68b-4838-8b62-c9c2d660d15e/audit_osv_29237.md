# [H] platform/x86: toshiba_acpi: Fix array out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2024-41028
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41028
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: toshiba_acpi: Fix array out-of-bounds access

In order to use toshiba_dmi_quirks[] together with the standard DMI
matching functions, it must be terminated by a empty entry.

Since this entry is missing, an array out-of-bounds access occurs
every time the quirk list is processed.

Fix this by adding the terminating empty entry.

## References
- https://git.kernel.org/stable/c/0d71da43d6b7916d36cf1953d793da80433c50bf
- https://git.kernel.org/stable/c/639868f1cb87b683cf830353bbee0c4078202313
- https://git.kernel.org/stable/c/b6e02c6b0377d4339986e07aeb696c632cd392aa
- https://git.kernel.org/stable/c/e030aa6c972641cb069086a8c7a0f747653e472a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41028.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
