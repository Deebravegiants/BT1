# [H] Prototype pollution in Snowboard framework

## Summary
Severity: High
Advisory: GHSA-3fh5-q6fg-w28q
CVE: CVE-2022-39357
CWE: CWE-1321
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-27
Source: https://github.com/advisories/GHSA-3fh5-q6fg-w28q
Type: github-advisory

## Affected
- Packagist: `wintercms/winter` — affected >=1.1.8 <1.1.10
- Packagist: `wintercms/winter` — affected >=1.2.0 <1.2.1

## Details
### Impact

The Snowboard framework in affected versions is vulnerable to prototype pollution in the main Snowboard class as well as its plugin loader. 

### Patches

This issue has been patched in https://github.com/wintercms/winter/commit/2a13faf99972e84c9661258f16c4750fa99d29a1 (for 1.2) and https://github.com/wintercms/winter/commit/bce4b59584abf961e9400af3d7a4fd7638e26c7f (for 1.1) and is available with Winter v1.1.10 and v1.2.1.

### Workarounds

If you have not yet upgraded, or are using the 1.1 branch of Winter (1.1.8 or above), you can avoid this issue by following some common security practices for JavaScript, including implementing a [content security policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) and auditing your scripts.

The 1.0 branch of Winter is not affected, as it does not contain the Snowboard framework.

### For more information

If you have any questions or comments about this advisory:

- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-3fh5-q6fg-w28q
- https://nvd.nist.gov/vuln/detail/CVE-2022-39357
- https://github.com/wintercms/winter/commit/2a13faf99972e84c9661258f16c4750fa99d29a1
- https://github.com/wintercms/winter/commit/bce4b59584abf961e9400af3d7a4fd7638e26c7f
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.1.10
- https://github.com/wintercms/winter/releases/tag/v1.2.1
