# [M] Denial of Service (DoS) vulnerability in RSSHub

## Summary
Severity: Medium
Advisory: GHSA-jvxx-v45p-v5vf
CVE: CVE-2022-31110
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-06-23
Source: https://github.com/advisories/GHSA-jvxx-v45p-v5vf
Type: github-advisory

## Affected
- npm: `rsshub` — affected >=0

## Details
### Impact

Passing some special values to the `filter` and `filterout` parameters can cause an abnormally high CPU. Impact on the performance of the servers and RSSHub services.

### Patches

It is fixed in 5c4177441417b44a6e45c3c63e9eac2504abeb5b , please update to this or the later versions as soon as possible.

### References

Full report: https://github.com/DIYgod/RSSHub/issues/10045

### For more information

If you have any questions or comments about this advisory:
* Open an issue in <https://github.com/DIYgod/RSSHub/issues>
* Email us at [i@diygod.me](mailto:i@diygod.me)

### Credits

@Rongronggg9

## References
- https://github.com/DIYgod/RSSHub/security/advisories/GHSA-jvxx-v45p-v5vf
- https://nvd.nist.gov/vuln/detail/CVE-2022-31110
- https://github.com/DIYgod/RSSHub/issues/10045
- https://github.com/DIYgod/RSSHub/commit/4671720f4c5e1aaaad8fcc1dce684b6546baf2ff
- https://github.com/DIYgod/RSSHub/commit/5c4177441417b44a6e45c3c63e9eac2504abeb5b
- https://github.com/DIYgod/RSSHub
