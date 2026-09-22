# [M] OpenCC  has an Out-of-bounds read when processing truncated UTF-8 input

## Summary
Severity: Medium
Advisory: GHSA-7fqq-q52p-2jjg
CWE: CWE-125
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-7fqq-q52p-2jjg
Type: github-advisory

## Affected
- npm: `opencc` — affected >=0 <1.2.0
- PyPI: `OpenCC` — affected >=0 <1.2.0

## Details
### Summary

OpenCC versions before 1.2.0 contain two `CWE-125: Out-of-bounds Read` issues caused by length validation failures in UTF-8 processing. When handling malformed or truncated UTF-8 input, OpenCC trusted derived length values without enforcing the invariant that processed length must not exceed the remaining input buffer. This could result in out-of-bounds reads during segmentation or conversion.

### Details

Two independent code paths in OpenCC failed to enforce the invariant:

`matchedLength <= remainingLength`

Both paths assumed derived length values were valid and within input bounds, but did not validate that assumption against the remaining buffer. This created the following failure chain:

`invalid UTF-8 -> incorrect derived length -> incorrect pointer advance -> remaining-length desynchronization -> out-of-bounds read`

In `MaxMatchSegmentation::Segment`, this could desynchronize remaining-length tracking and cause out-of-bounds reads during prefix matching.

In `Conversion::Convert(const char*)`, similar logic could advance processing past the end of the input string and read beyond the null terminator into adjacent memory. In some cases, unintended heap bytes could be propagated into the conversion result.

PR #1005 fixes both issues by explicitly tracking input boundaries, recomputing remaining length on each iteration, and clamping processed lengths so the buffer-bound invariant is preserved.

Affected versions:

* All versions before 1.2.0

Patched version:

* 1.2.0

### PoC

Build a vulnerable version with AddressSanitizer enabled and process input ending with a truncated UTF-8 sequence, such as a missing final byte of a 3-byte character. The original report and ASan reproduction are available in [Issue #997](https://github.com/BYVoid/OpenCC/issues/997).

### Impact

This vulnerability may cause process crashes and limited, non-deterministic information disclosure when OpenCC processes malformed or attacker-controlled UTF-8 input. The issue does not indicate arbitrary write or code execution.

OpenCC is distributed through system and language-specific package managers, prebuilt binaries, container images, and downstream software, so affected versions may be present even when it is not listed as a direct dependency. Users should upgrade all installed or bundled copies of OpenCC to 1.2.0 or later.

### Credit

OpenCC thanks @oneafter for reporting the issue.

## References
- https://github.com/BYVoid/OpenCC/security/advisories/GHSA-7fqq-q52p-2jjg
- https://github.com/BYVoid/OpenCC/issues/997
- https://github.com/BYVoid/OpenCC/pull/1005
- https://github.com/BYVoid/OpenCC
- https://github.com/BYVoid/OpenCC/releases/tag/ver.1.2.0
