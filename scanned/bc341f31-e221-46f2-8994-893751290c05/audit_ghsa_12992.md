# [H] Unsanitized user controlled input in module generation

## Summary
Severity: High
Advisory: GHSA-f8pq-3926-8gx5
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-f8pq-3926-8gx5
Type: github-advisory

## Affected
- npm: `@opentelemetry/instrumentation` — affected >=0.40.0 <0.41.2

## Details
## Impact

The `import-in-the-middle` loader used by `@opentelemetry/instrumentation` works by generating a wrapper module on the fly. The wrapper uses the module specifier to load the original module and add some wrapping code. It allows for remote code execution in cases where an application passes user-supplied input directly to an `import()` function.

## Patches

This vulnerability has been patched in `@opentelemetry/instrumentation` version `0.41.2`

## Workarounds

- Do not pass any user-supplied input to `import()`. Instead, verify it against a set of allowed values.
- If using `@opentelemetry/instrumentation` with support for EcmaScript Modules is not needed, ensure that none of the following options are set (either via command-line or the `NODE_OPTIONS` environment variable):
```
--experimental-loader=@opentelemetry/instrumentation/hook.mjs
--experimental-loader @opentelemetry/instrumentation/hook.mjs
--loader=import-in-the-middle/hook.mjs
--loader import-in-the-middle/hook.mjs
```

## References

- https://github.com/DataDog/import-in-the-middle/security/advisories/GHSA-5r27-rw8r-7967

## References
- https://github.com/open-telemetry/opentelemetry-js/security/advisories/GHSA-f8pq-3926-8gx5
- https://github.com/open-telemetry/opentelemetry-js/commit/ffe641c08c69f41ca8d292221dc1804d511efb28
- https://github.com/open-telemetry/opentelemetry-js
