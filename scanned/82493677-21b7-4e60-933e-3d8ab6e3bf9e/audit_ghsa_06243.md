# [H] Glances: `--disable-config-exec` does not cover on-alert action commands (incomplete fix of CVE-2026-53925)

## Summary
Severity: High
Advisory: GHSA-59fj-m2j6-hcxh
CVE: CVE-2026-68519
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-59fj-m2j6-hcxh
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.6

## Details
## Summary
In Glances 4.5.5 the `--disable-config-exec` flag was extended (GHSA-3vwc-qwhc-3mj7) to stop `secure_popen()` from
interpreting the shell operators `&&`, `|` and `>` in **AMP** command values taken from the configuration file. The
hardening was not applied to the **on-alert action** command path, which reads its command lines from the same
configuration file. As a result, with `--disable-config-exec` enabled, a configured alert action that contains `>`
(file redirection), `&&` (chaining) or `|` (pipe) still has those operators interpreted, allowing arbitrary file
write / command chaining at the privilege of the glances process when the alert triggers.

## Affected code
`glances/actions.py` (Glances 4.5.5, latest):
```python
ret = secure_popen(cmd_full)        # line 111 — no allow_operators=, defaults to True
```
By contrast the AMP modules were fixed:
```python
# glances/amps/default/__init__.py:69
self.set_result(secure_popen(res, allow_operators=self.allow_operators()).rstrip())
# glances/amps/systemv/__init__.py:60
res = secure_popen(self.get('service_cmd'), allow_operators=self.allow_operators())
```

## PoC (benign)
`glances.conf`:
```ini
[cpu]
user_critical=1
user_critical_action=echo MARKER > /tmp/poc_marker
```
Run `glances --disable-config-exec` and generate CPU load. When the cpu `user` alert reaches CRITICAL, `/tmp/poc_marker`
is created — i.e. the `>` operator was interpreted despite `--disable-config-exec`. The same `>` in an `[amp_*]`
`command` value is correctly *not* interpreted.

## Impact
Arbitrary file write (`>`), command chaining (`&&`) and pipe (`|`) from config-defined alert actions, contrary to the
guarantee of `--disable-config-exec`. Trust boundary = the glances configuration file.

## Suggested fix
Pass `allow_operators=not args.disable_config_exec` from `GlancesActions.run()` into `secure_popen()` (GlancesActions
already holds `args`).

## Credit
Reported via responsible-disclosure incomplete-fix measurement study.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-59fj-m2j6-hcxh
- https://github.com/nicolargo/glances/commit/5c07c0d96423e9d5b9de71dd92e3717c66f504bd
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.6
