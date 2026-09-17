# [C] UEFI Firmware Parser has a stack out-of-bounds write in tiano decompressor MakeTable

## Summary
Severity: Critical
Advisory: GHSA-2689-5p89-6j3j
CVE: CVE-2026-54333
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-2689-5p89-6j3j
Type: github-advisory

## Affected
- PyPI: `uefi-firmware` — affected >=0

## Details
`uefi-firmware` contains a stack out-of-bounds write vulnerability in the native tiano/EFI decompressor. in `uefi_firmware/compression/Tiano/Decompress.c`, `MakeTable()` does not validate that bit-length values read from the compressed bitstream are within the expected range (`0..16`). a crafted firmware blob can supply bit lengths greater than `16`, causing out-of-bounds writes to the stack-allocated `Count[17]` array and related decode tables.

reachability is through the normal parsing path: `CompressedSection.process()` -> `efi_compressor.TianoDecompress()` -> `TianoDecompress()` -> `ReadPTLen()` -> `MakeTable()`.

Minimum impact is a deterministic crash; depending on build/runtime details, the stack memory corruption may be exploitable for code execution in the context of the parsing process. this project shipped its own copy of the decompressor without the upstream EDK2 hardening for this bug class.

References:

- PR: <https://github.com/theopolis/uefi-firmware-parser/pull/145>
- fix commit: <https://github.com/theopolis/uefi-firmware-parser/commit/bf3dfaa8a05675bae6ea0cbfa082ddcebfcde23e>
- upstream related fixes: CVE-2017-5731, CVE-2017-5732, CVE-2017-5733, CVE-2017-5734, CVE-2017-5735

## References
- https://github.com/theopolis/uefi-firmware-parser/security/advisories/GHSA-2689-5p89-6j3j
- https://github.com/theopolis/uefi-firmware-parser/pull/145
- https://github.com/theopolis/uefi-firmware-parser/commit/bf3dfaa8a05675bae6ea0cbfa082ddcebfcde23e
- https://github.com/theopolis/uefi-firmware-parser
