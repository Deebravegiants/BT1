# [H] Symfony has Unauthenticated PHP Object Deserialization in MonologBridge server:log Listener

## Summary
Severity: High
Advisory: GHSA-m7v2-7gxm-vc2v
CVE: CVE-2026-45077
CWE: CWE-502, CWE-668
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-m7v2-7gxm-vc2v
Type: github-advisory

## Affected
- Packagist: `symfony/monolog-bridge` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/monolog-bridge` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/monolog-bridge` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/monolog-bridge` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

`Symfony\Bridge\Monolog\Command\ServerLogCommand` (the `server:log` console command) is a development-time helper that opens a TCP listener and displays log records pushed to it by the application's logging pipeline. Two unsafe defaults combine into a remotely reachable PHP object-deserialization sink:

1. The listener binds to `0.0.0.0:9911` by default; it accepts connections on every interface, not only loopback.
2. Each received frame is processed as `unserialize(base64_decode($message))` without an `allowed_classes` allowlist, without authentication, and without any integrity check. The decoded value is then passed to `displayLog(..., array $record)` which assumes (without validating) that the result is an array.

Any host that can reach TCP port 9911 on a machine running `server:log` can therefore submit attacker-chosen serialized PHP payloads. The minimum impact is an unauthenticated denial of service (sending a non-array, e.g. `serialize(new stdClass())`, crashes the listener with a type error). Object injection with magic-method side effects (`__wakeup()` / `__destruct()` / etc.) is reachable before the array type-check fires; full remote code execution is environment-dependent and contingent on usable gadget chains in the autoload set of the target process.

### Resolution

The `server:log` command no longer binds to all interfaces by default: the default `--host` is now `127.0.0.1:9911`, requiring explicit opt-in to accept off-host traffic. Message decoding is gated by an `unserialize()` allowlist restricted to the `Symfony\Component\VarDumper\Caster\*` and `Symfony\Component\VarDumper\Cloner\*` classes that legitimately appear inside dumped log records; any other class is rejected and the record discarded.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/0891b2f293896c488e26943dc034334364b77fc4) for branch 5.4.

### Credits

Symfony would like to thank Toàn Thắng and Sam Sanoop for reporting the issue and Nicolas Grekas for fixing it.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-m7v2-7gxm-vc2v
- https://github.com/symfony/symfony/commit/0891b2f293896c488e26943dc034334364b77fc4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/monolog-bridge/CVE-2026-45077.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45077.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45077
