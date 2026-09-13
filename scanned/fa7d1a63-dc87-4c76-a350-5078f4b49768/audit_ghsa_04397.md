# [H] spomky-labs/otphp: Unbounded digits parameter in a provisioning URI triggers an uncaught DivisionByZeroError in OTP generation

## Summary
Severity: High
Advisory: GHSA-g7m4-839x-ch6v
CWE: CWE-1284, CWE-369
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-g7m4-839x-ch6v
Type: github-advisory

## Affected
- Packagist: `spomky-labs/otphp` — affected >=0 <11.4.3

## Details
## Summary

The `digits` parameter parsed from a provisioning URI is validated only with a lower bound (`$value > 0`) and has no upper bound (`src/OTP.php:353-357`). OTP generation computes `$code % (10 ** $this->getDigits())` (`src/OTP.php:283`). When `digits` is large enough that `10 ** digits` overflows PHP's integer range and the `(int)` cast yields `0` (around `digits >= 40` on 64-bit PHP 8.x), the modulo operand becomes `0` and PHP raises a `DivisionByZeroError`.

## Impact

`OTPHP\Factory::loadFromProvisioningUri()` forwards the attacker-controlled `digits` query value to `setParameter('digits', $value)`, so a hostile URI such as `otpauth://totp/Alice?secret=JBSWY3DPEHPK3PXP&digits=50` produces an OTP object whose `at()`, `now()`, and `verify()` all throw `DivisionByZeroError`. Because `DivisionByZeroError` extends `Error` (not `Exception`), callers that guard OTP generation with a `catch (\Exception)` do not catch it, turning a malformed URI into an unhandled fatal error (denial of service of the verification path).

Measured threshold on PHP 8.3: `digits = 30` works, `digits >= 40` throws `DivisionByZeroError: Modulo by zero`.

## Affected component

- `src/OTP.php:353-357` — `digits` parameter callback (no upper bound)
- `src/OTP.php:283` — `$code % (10 ** $this->getDigits())`

## Proof of concept

```php
use OTPHP\Factory;
use OTPHP\InternalClock;

$otp = Factory::loadFromProvisioningUri(
    'otpauth://totp/Alice?secret=JBSWY3DPEHPK3PXP&digits=50',
    new InternalClock()
);
$otp->at(0); // DivisionByZeroError: Modulo by zero (escapes catch (\Exception))
```

## Remediation

Enforce a sane upper bound on `digits` in the parameter validation callback (e.g. reject values above 8–10, the practical range for OTPs) so that an out-of-range value is rejected with a documented exception instead of producing an object that fails later with an uncatchable `Error`.

## References
- https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-g7m4-839x-ch6v
- https://github.com/FriendsOfPHP/security-advisories/blob/master/spomky-labs/otphp/GHSA-g7m4-839x-ch6v.yaml
- https://github.com/Spomky-Labs/otphp
