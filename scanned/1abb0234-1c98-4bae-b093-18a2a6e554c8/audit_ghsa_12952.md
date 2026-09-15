# [H] import-in-the-middle has unsanitized user controlled input in module generation

## Summary
Severity: High
Advisory: GHSA-5r27-rw8r-7967
CVE: CVE-2023-38704
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-08-08
Source: https://github.com/advisories/GHSA-5r27-rw8r-7967
Type: github-advisory

## Affected
- npm: `import-in-the-middle` — affected >=0 <1.4.2

## Details
### Impact
The `import-in-the-middle` loader works by generating a wrapper module on the fly. The wrapper uses the module specifier to load the original module and add some wrapping code. It allows for remote code execution in cases where an application passes user-supplied input directly to an import() function.

### Patches
This vulnerability has been patched in `import-in-the-middle` version 1.4.2

### Workarounds
* Do not pass any user-supplied input to `import()`. Instead, verify it against a set of allowed values.
* If using `import-in-the-middle` and support for EcmaScript Modules is not needed, ensure that none of the following options are set (either via command-line or the `NODE_OPTIONS` environment variable):
```
--loader=import-in-the-middle/hook.mjs
--loader import-in-the-middle/hook.mjs
```

### References
If you have any questions or comments about this advisory, email us at [security@datadoghq.com](mailto:security@datadoghq.com)

## References
- https://github.com/DataDog/import-in-the-middle/security/advisories/GHSA-5r27-rw8r-7967
- https://nvd.nist.gov/vuln/detail/CVE-2023-38704
- https://github.com/DataDog/import-in-the-middle/commit/2531cdd9d1d73f9eaa87c16967f60cb276c1971b
- https://github.com/DataDog/import-in-the-middle
