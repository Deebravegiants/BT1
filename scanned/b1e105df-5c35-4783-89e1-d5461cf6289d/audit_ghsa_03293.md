# [M] Credential leak in react-native-fast-image

## Summary
Severity: Medium
Advisory: GHSA-6xhg-q9c8-rj32
CVE: CVE-2020-7696
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-6xhg-q9c8-rj32
Type: github-advisory

## Affected
- npm: `react-native-fast-image` — affected >=0 <8.3.0

## Details
This affects all versions before version 8.3.0 of package react-native-fast-image. When an image with `source={{uri: "...", headers: { host: "somehost.com", authorization: "..." }}` is loaded, all other subsequent images will use the same headers, this can lead to signing credentials or other session tokens being leaked to other servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7696
- https://github.com/DylanVann/react-native-fast-image/issues/690
- https://github.com/DylanVann/react-native-fast-image/pull/691
- https://github.com/DylanVann/react-native-fast-image/commit/4a7cd64f5b0aa40b04d63ccb105ee2b511abe624
- https://snyk.io/vuln/SNYK-JS-REACTNATIVEFASTIMAGE-572228
