# [M] Unsafe Identifiers in Opencast

## Summary
Severity: Medium
Advisory: GHSA-w29m-fjp4-qhmq
CVE: CVE-2020-5230
CWE: CWE-99
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-w29m-fjp4-qhmq
Type: github-advisory

## Affected
- Maven: `org.opencastproject:base` — affected >=0 <7.6
- Maven: `org.opencastproject:base` — affected >=8.0 <8.1

## Details
### Impact

Opencast allows almost arbitrary identifiers for media packages and
elements to be used. This can be problematic for operation and security
since such identifiers are sometimes used for file system operations
which may lead to an attacker being able to escape working directories and
write files to other locations.

In addition, Opencast's Id.toString(…) vs Id.compact(…) behavior,
the latter trying to mitigate some of the file system problems, can
cause errors due to identifier mismatch since an identifier may
unintentionally change.

### Patches

This issue is fixed in Opencast 7.6 and 8.1.

### Workarounds

There is no workaround for this.

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [opencast/opencast](https://github.com/opencast/opencast/issues)
- For security-relevant information, email us at security@opencast.org

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-w29m-fjp4-qhmq
- https://nvd.nist.gov/vuln/detail/CVE-2020-5230
- https://github.com/opencast/opencast/commit/bbb473f34ab95497d6c432c81285efb0c739f317
