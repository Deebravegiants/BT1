# [M] spomky-labs/otphp: Mass-assignment in Factory::loadFromProvisioningUri lets a hostile provisioning URI corrupt OTP state or leak an uncaught TypeError

## Summary
Severity: Medium
Advisory: GHSA-2jx3-65f3-xr8r
CWE: CWE-915
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2jx3-65f3-xr8r
Type: github-advisory

## Affected
- Packagist: `spomky-labs/otphp` — affected >=0 <11.4.3

## Details
## Summary

`OTPHP\Factory::loadFromProvisioningUri()` parses an attacker-supplied `otpauth://` URI and forwards **every** query key to `OTP::setParameter($key, $value)`. `setParameter()` resolves the name with `property_exists($this, $parameter)` and performs a dynamic write `$this->{$parameter} = $value` (`src/OTP.php:196-197`). Because the query keys are entirely controlled by whoever produced the URI, a URI can target the internal properties of the OTP object that are not meant to be set from a URI: `parameters`, `issuer`, `label`, `issuer_included_as_parameter`, and (on TOTP) the readonly `clock`. This is an instance of object property mass-assignment (CWE-915).

## Impact

The `Factory` is documented as the entry point for third-party provisioning URIs (e.g. QR codes from Microsoft 365 / Google Authenticator). An application that loads such a URI is exposed to:

- **State corruption.** A URI such as `otpauth://totp/Alice?secret=JBSWY3DPEHPK3PXP&parameters[foo]=bar` overwrites the whole internal `$parameters` array that `createFromSecret()` primed (`period`, `algorithm`, `digits`, `epoch`). The resulting object is silently unusable: `getProvisioningUri()`, `getDigits()`, `at()`, `verify()` then throw `ParameterNotFoundException`.
- **Uncaught TypeError escaping the documented exception type.** A URI such as `otpauth://totp/Alice?secret=JBSWY3DPEHPK3PXP&issuer_included_as_parameter=notabool` assigns a string to a typed `bool` property and raises a `TypeError`. The `try/catch` in `loadFromProvisioningUri()` only wraps `Url::fromString()`; `createOTP()` and `populateOTP()` run outside it, so the `TypeError` (and `Error` on the readonly `clock`) escapes past the documented `InvalidProvisioningUriException`, breaking callers that catch only the documented type.
- **Label/issuer validation bypass.** `parameters[label]=hijacked` stores a label into the parameters array without running the `label` validation callback (keyed on `label`, not `parameters`). `getLabel()` and `getParameter('label')` then disagree — a confused-deputy risk.

## Affected component

- `src/OTP.php:187-201` — `setParameter()` dynamic property write
- `src/Factory.php:50-55` — `populateParameters()` forwarding all query keys

## Proof of concept

```php
use OTPHP\Factory;

// State corruption
$otp = Factory::loadFromProvisioningUri(
    'otpauth://totp/Alice?secret=JBSWY3DPEHPK3PXP&parameters[foo]=bar',
    $clock
);
$otp->getProvisioningUri(); // ParameterNotFoundException: Parameter "period" does not exist

// Uncaught TypeError
Factory::loadFromProvisioningUri(
    'otpauth://totp/Alice?secret=JBSWY3DPEHPK3PXP&issuer_included_as_parameter=notabool',
    $clock
); // TypeError escapes InvalidProvisioningUriException
```

## Remediation

Restrict the keys accepted from a provisioning URI to a known allow-list of public OTP parameters, and never let a URI key resolve to an internal object property via `property_exists`. Route all URI-sourced values through the validated parameter map only.

## References
- https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-2jx3-65f3-xr8r
- https://github.com/FriendsOfPHP/security-advisories/blob/master/spomky-labs/otphp/GHSA-2jx3-65f3-xr8r.yaml
- https://github.com/Spomky-Labs/otphp
