# [C] Remote Code Execution in paginator

## Summary
Severity: Critical
Advisory: GHSA-w98m-2xqg-9cvj
CVE: CVE-2020-15150
Ecosystem: Hex
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-w98m-2xqg-9cvj
Type: github-advisory

## Affected
- Hex: `paginator` — affected >=0 <1.0.0

## Details
There is a vulnerability in Paginator which makes it susceptible to Remote Code Execution (RCE) attacks via input parameters to the `paginate()` function.

### Impact
There is a vulnerability in Paginator which makes it susceptible to Remote Code Execution (RCE) attacks via input parameters to the `paginate()` function. This will potentially affect all current users of `Paginator` prior to version >= 1.0.0.

### Patches
The vulnerability has been patched in version 1.0.0 and all users should upgrade to this version immediately. Note that this patched version uses a dependency that requires an Elixir version >=1.5.

### Credits

Thank you to Peter Stöckli.

## References
- https://github.com/duffelhq/paginator/security/advisories/GHSA-w98m-2xqg-9cvj
- https://nvd.nist.gov/vuln/detail/CVE-2020-15150
- https://github.com/duffelhq/paginator/commit/bf45e92602e517c75aea0465efc35cd661d9ebf8
- https://github.com/duffelhq/paginator
- https://github.com/duffelhq/paginator/blob/ccf0f37fa96347cc8c8a7e9eb2c64462cec4b2dc/README.md#security-considerations
- https://hex.pm/packages/paginator
