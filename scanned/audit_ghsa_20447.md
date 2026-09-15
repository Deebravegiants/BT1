# [H] Denial of service in CBOR library

## Summary
Severity: High
Advisory: GHSA-fj2w-wfgv-mwq6
CVE: CVE-2024-23684
CWE: CWE-407
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-fj2w-wfgv-mwq6
Type: github-advisory

## Affected
- Maven: `com.upokecenter:cbor` — affected >=4.0.0 <4.5.1

## Details
### Impact
Due to this library's use of an inefficient algorithm, it is vulnerable to a denial of service attack when a maliciously crafted input is passed to `DecodeFromBytes` or other CBOR decoding mechanisms in this library.  

Affected versions _include_ versions 4.0.0 through 4.5.0.

This vulnerability was privately reported to me.

### Patches
This issue has been fixed in version 4.5.1.  Users should use the latest version of this library.  (The latest version is not necessarily 4.5.1.  Check the README for [this library's repository](https://github.com/peteroupc/CBOR-Java) to see the latest version's version number.)

### Workarounds

Again, users should use the latest version of this library.

In the meantime, note that the inputs affected by this issue are all CBOR maps or contain CBOR maps.  An input that decodes to a single CBOR object is not capable of containing a CBOR map if&mdash;

- it begins with a byte other than 0x80 through 0xDF, or
- it does not contain a byte in the range 0xa0 through 0xBF.

Such an input is not affected by this vulnerability and an application can choose to perform this check before passing it to a CBOR decoding mechanism.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the CBOR repository](https://github.com/peteroupc/CBOR-Java).

## References
- https://github.com/peteroupc/CBOR-Java/security/advisories/GHSA-fj2w-wfgv-mwq6
- https://nvd.nist.gov/vuln/detail/CVE-2024-23684
- https://github.com/peteroupc/CBOR-Java
- https://vulncheck.com/advisories/vc-advisory-GHSA-fj2w-wfgv-mwq6
