# [M] Memory leak in Nanopb

## Summary
Severity: Medium
Advisory: GHSA-85rr-4rh9-hhwh
CVE: CVE-2020-26243
CWE: CWE-119, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-11-25
Source: https://github.com/advisories/GHSA-85rr-4rh9-hhwh
Type: github-advisory

## Affected
- PyPI: `nanopb` — affected >=0.3.2 <0.3.9.7
- PyPI: `nanopb` — affected >=0.4.0 <0.4.4

## Details
### Impact
Decoding specifically formed message can leak memory if dynamic allocation is enabled and an oneof field contains a static submessage that contains a dynamic field, and the message being decoded contains the submessage multiple times. This is rare in normal messages, but it is a concern when untrusted data is parsed.

### Patches
Preliminary patch is [available on git](https://github.com/nanopb/nanopb/commit/edf6dcbffee4d614ac0c2c1b258ab95185bdb6e9) and problem will be patched in versions 0.3.9.7 and 0.4.4 once testing has been completed.

### Workarounds
Following workarounds are available:
* Set the option `no_unions` for the oneof field. This will generate fields as separate instead of C union, and avoids triggering the problematic code.
* Set the type of the submessage field inside oneof to `FT_POINTER`. This way the whole submessage will be dynamically allocated and the problematic code is not executed.
* Use an arena allocator for nanopb, to make sure all memory can be released afterwards.

### References
Bug report: https://github.com/nanopb/nanopb/issues/615

### For more information
If you have any questions or comments about this advisory, comment on the bug report linked above.

## References
- https://github.com/nanopb/nanopb/security/advisories/GHSA-85rr-4rh9-hhwh
- https://nvd.nist.gov/vuln/detail/CVE-2020-26243
- https://github.com/nanopb/nanopb/issues/615
- https://github.com/nanopb/nanopb/commit/4fe23595732b6f1254cfc11a9b8d6da900b55b0c
- https://github.com/nanopb/nanopb/blob/2b48a361786dfb1f63d229840217a93aae064667/CHANGELOG.txt
