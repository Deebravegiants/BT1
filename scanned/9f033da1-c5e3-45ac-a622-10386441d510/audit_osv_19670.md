# [C] CVE-2021-23518

## Summary
Severity: Critical
Advisory: CVE-2021-23518
Aliases: GHSA-wg6g-ppvx-927h
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-23518
Type: osv

## Details
The package cached-path-relative before 1.1.0 are vulnerable to Prototype Pollution via the cache variable that is set as {} instead of Object.create(null) in the cachedPathRelative function, which allows access to the parent prototype properties when the object is used to create the cached relative path. When using the origin path as __proto__, the attribute of the object is accessed instead of a path. **Note:** This vulnerability derives from an incomplete fix in https://security.snyk.io/vuln/SNYK-JS-CACHEDPATHRELATIVE-72573

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00006.html
- https://github.com/ashaffer/cached-path-relative/commit/40c73bf70c58add5aec7d11e4f36b93d144bb760
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2348246
- https://snyk.io/vuln/SNYK-JS-CACHEDPATHRELATIVE-2342653
