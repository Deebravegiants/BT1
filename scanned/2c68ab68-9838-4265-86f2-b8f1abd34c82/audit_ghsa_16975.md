# [H] DIRAC: Unauthorized users can read proxy contents during generation

## Summary
Severity: High
Advisory: GHSA-v6f3-gh5h-mqwx
CVE: CVE-2024-29905
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-v6f3-gh5h-mqwx
Type: github-advisory

## Affected
- PyPI: `DIRAC` — affected >=0 <8.0.41

## Details
### Impact

During the proxy generation process (e.g., when using `dirac-proxy-init`) it is possible for unauthorized users on the same machine to gain read access to the proxy. This allows the user to then perform any action that is possible with the original proxy.

This vulnerability only exists for a short period of time (sub-millsecond) during the generation process.

### Patches

_Has the problem been patched? What versions should users upgrade to?_

### Workarounds

Setting the `X509_USER_PROXY` environment variable to a path that is inside a directory that is only readable to the current user avoids the potential risk. After the file has been written it can be safely copied to the standard location (`/tmp/x509up_uNNNN`).

### References

## References
- https://github.com/DIRACGrid/DIRAC/security/advisories/GHSA-v6f3-gh5h-mqwx
- https://nvd.nist.gov/vuln/detail/CVE-2024-29905
- https://github.com/DIRACGrid/DIRAC/commit/1faa709341969a6321e29c843ca94039d33b2c3d
- https://github.com/DIRACGrid/DIRAC
