# [H] nanopb vulnerable to invalid free() call with oneofs and PB_ENABLE_MALLOC

## Summary
Severity: High
Advisory: GHSA-7mv5-5mxh-qg88
CVE: CVE-2021-21401
CWE: CWE-763
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2024-08-30
Source: https://github.com/advisories/GHSA-7mv5-5mxh-qg88
Type: github-advisory

## Affected
- PyPI: `nanopb` — affected >=0.3.2 <0.3.9.8
- PyPI: `nanopb` — affected >=0.4.0 <0.4.5

## Details
### Impact
Decoding a specifically formed message can cause invalid `free()` or `realloc()` calls if the message type contains an `oneof` field, and the `oneof` directly contains both a pointer field and a non-pointer field. If the message data first contains the non-pointer field and then the pointer field, the data of the non-pointer field is incorrectly treated as if it was a pointer value. Such message data rarely occurs in normal messages, but it is a concern when untrusted data is parsed.

### Patches
Preliminary patch is available on git for [0.4.x](https://github.com/nanopb/nanopb/commit/e2f0ccf939d9f82931d085acb6df8e9a182a4261) and [0.3.x](https://github.com/nanopb/nanopb/commit/4a375a560651a86726e5283be85a9231fd0efe9c) branches. The fix will be released in versions 0.3.9.8 and 0.4.5 once testing has been completed.

### Workarounds
Following workarounds are available:
* Set the option `no_unions` for the oneof field. This will generate fields as separate instead of C union, and avoids triggering the problematic code.
* Set the type of all fields inside the oneof to `FT_POINTER`. This ensures that the data contained inside the `union` is always a valid pointer.
* Heap implementations that guard against invalid `free()` provide a partial mitigation. Depending on the message type, the pointer value may be attacker controlled and can be used to bypass heap protections.

### References
Bug report: https://github.com/nanopb/nanopb/issues/647

### For more information
If you have any questions or comments about this advisory, comment on the bug report linked above.

## References
- https://github.com/nanopb/nanopb/security/advisories/GHSA-7mv5-5mxh-qg88
- https://nvd.nist.gov/vuln/detail/CVE-2021-21401
- https://github.com/nanopb/nanopb/issues/647
- https://github.com/nanopb/nanopb/commit/4a375a560651a86726e5283be85a9231fd0efe9c
- https://github.com/nanopb/nanopb/commit/e2f0ccf939d9f82931d085acb6df8e9a182a4261
- https://github.com/nanopb/nanopb
- https://github.com/nanopb/nanopb/blob/c9124132a604047d0ef97a09c0e99cd9bed2c818/CHANGELOG.txt#L1
- https://github.com/pypa/advisory-database/tree/main/vulns/nanopb/PYSEC-2021-432.yaml
