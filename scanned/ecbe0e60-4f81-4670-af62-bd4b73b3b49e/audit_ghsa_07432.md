# [M] PocketSphinx: Buffer overflows in language and acoustic model loading code

## Summary
Severity: Medium
Advisory: GHSA-56r5-2p2f-7cxp
CVE: CVE-2026-54559
CWE: CWE-119, CWE-121, CWE-122
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-56r5-2p2f-7cxp
Type: github-advisory

## Affected
- PyPI: `pocketsphinx` — affected >=0 <5.1.1

## Details
### Impact

The trie language model code introduced in PocketSphinx 5prealpha failed to check various boundary conditions when reading the headers of ARPA, DMP, and binary format language model files.  In the case of invalid, corrupted or malicious input files, this could lead to stack and heap buffer overflows.

In addition, the acoustic model loading code (which is over 30 years old...) contains numerous instances of `sscanf` with an unbounded string field which could also lead to stack overflows in the case of corrupt or malicious inputs.

Because PocketSphinx will search the directory given by the `POCKETSPHINX_PATH` environment variable for acoustic and language model files, if this directory is writable by untrusted users, an attacker could corrupt an existing file or write a malicious one to this directory in order to trigger the vulnerability.

### Patches

The problem has been corrected in PocketSphinx 5.1.1.

There is no patch currently available for users of Pocketsphinx 5prealpha, who are encouraged to migrate as soon as possible to  PocketSphinx 5.1.1.

### Workarounds

Ensure that the `POCKETSPHINX_PATH` environment variable is either unset, or set to a directory whose contents are trusted and which cannot be written by untrusted users.

## References
- https://github.com/cmusphinx/pocketsphinx/security/advisories/GHSA-56r5-2p2f-7cxp
- https://github.com/cmusphinx/pocketsphinx
- https://github.com/cmusphinx/pocketsphinx/releases/tag/v5.1.1
