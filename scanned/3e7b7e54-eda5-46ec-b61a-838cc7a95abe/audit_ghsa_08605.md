# [M] Flight has path traversal in `make:controller` CLI that creates arbitrary directories outside project root

## Summary
Severity: Medium
Advisory: GHSA-3xjv-pmf2-gf2q
CVE: CVE-2026-42549
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-3xjv-pmf2-gf2q
Type: github-advisory

## Affected
- Packagist: `flightphp/core` — affected >=0 <3.18.1

## Details
### Summary
The `make:controller` CLI command calls `mkdir(..., recursive: true)` on a path built from the user-supplied controller name, **before** Nette's class-name validation runs. The class-file write is correctly rejected by Nette when the name contains `/`, but the recursive directory creation side effect is already committed — including directories located outside the project root through `../` traversal.

### Affected code
`flight/commands/ControllerCommand.php` (≈ 63-66):

```php
if (is_dir(dirname($controllerPath)) === false) {
    $io->info('Creating directory ' . dirname($controllerPath), true);
    mkdir(dirname($controllerPath), 0755, true);   // un-normalized, runs before validation
}
```

### Proof of concept
```
$ php vendor/flightphp/runway/runway make:controller '../../../../tmp/CONTROLLER_TRAVERSAL_TEST/pwn'
Creating directory .../app/controllers/../../../../tmp/CONTROLLER_TRAVERSAL_TEST
Nette\InvalidArgumentException: Value '../../../../tmp/CONTROLLER_TRAVERSAL_TEST/pwnController' is not valid class name.

$ ls /home/user/tmp/CONTROLLER_TRAVERSAL_TEST
(directory exists — created before the exception was thrown)
```

### Impact
- **Arbitrary directory creation outside the project root**, executable by any local actor that can run the Flight CLI (developer machine, shared CI build agent, compromised dev container).
- Primes log-file planting for chained LFI exploitation (e.g. creating a directory where an attacker can later drop a `.php` file to be included via a distinct template-include weakness).
- On Windows, the `\` separator opens additional traversal surface.

### Patch (fixed in `3.18.1`, commit `b8dd23a`)
The controller name is now normalized with `basename()` and validated against `^[A-Za-z_][A-Za-z0-9_]*$` before any `mkdir` side effect runs.

### Credit
Discovered by **@Rootingg**.

## References
- https://github.com/flightphp/core/security/advisories/GHSA-3xjv-pmf2-gf2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-42549
- https://github.com/flightphp/core
