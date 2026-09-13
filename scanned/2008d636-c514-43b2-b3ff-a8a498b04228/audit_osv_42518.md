# [H] ASoC: tas2781: bound firmware description string parsing

## Summary
Severity: High
Advisory: CVE-2026-68348
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68348
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: tas2781: bound firmware description string parsing

The TAS2781 firmware parser reads several variable-length description
strings with strlen() before checking that the string terminator is
present inside the firmware blob. A malformed firmware image without a
NUL terminator can therefore make the parser walk past the end of the
firmware buffer before the later size checks run.

Add a small bounded string-length helper and use it for all description
fields that are parsed from the firmware buffer. Keep the existing size
checks for the fixed bytes that follow each string.

## References
- https://git.kernel.org/stable/c/0ec45e80a82785ee147516fdecf5c93707dec119
- https://git.kernel.org/stable/c/3ddb0d3e36507615e5ef010a879357a54870adf5
- https://git.kernel.org/stable/c/41ae2b7d37c3dd82302167496836cca9f0328374
- https://git.kernel.org/stable/c/bc889dfcea9294a1eae7f8e2f3573a90764ae4d0
- https://git.kernel.org/stable/c/e75ef37d83c90b09bedb601624b47e168202b226
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68348.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68348
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
