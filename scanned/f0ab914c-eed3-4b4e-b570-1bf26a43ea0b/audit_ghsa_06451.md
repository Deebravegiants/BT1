# [H] Linuxfabrik Monitoring Plugins have local privilege escalation using embedded command

## Summary
Severity: High
Advisory: GHSA-798h-hpph-m24j
CVE: CVE-2026-55426
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-798h-hpph-m24j
Type: github-advisory

## Affected
- PyPI: `linuxfabrik-lib` — affected >=0 <5.0.0

## Details
### Summary
When a check plugin places user provided input inside a command which is passed to `shell_exec`, an attacker can abuse this to run arbitrary commands. This is mainly dangerous for plugins which are listed in the sudoers file, because this allows an attacker controlling the nagios user to get root privileges.

### Details
An example for this is the `restic-check` plugin, where the `--repo` argument is placed inside the command argument of `shell_exec`. As an example, an attacker could use the `--repo` argument `|touch /root/nagios-was-here|`. The full restic command is assembled to the string `restic --json --repo=|touch /root/nagios-was-here| --password-file= check` before it is passed to `shell_exec`. `shell_exec` then splits the command up in three parts at the | boundaries and executes the parts separately, which also executes the embedded command `touch /root/nagios-was-here`.

### PoC
This PoC shows how the nagios user can use this to create a file inside `/root`.
```
nagios@test-vm:/$ sudo /usr/lib64/nagios/plugins/restic-check --repo '|touch /root/nagios-was-here|'
```

### Impact
The vulnerability is a local privilege escalation.

### Fix

#### Switch from | to an array
Remove the | split functionality. Instead, modify shell_exec to accept either a string or an array of strings. If an array is provided, the commands are chained together like they currently are when using |. If a string is provided, no split should be performed. You could also introduce a separate function like `shell_exec_with_user_input()` which implements this such that the current shell_exec function can stay like it is.

This leaves the problem that an attacker can still specify arbitrary arguments inside a command. An example for this would be to use the `--repo` argument `sftp://example.com --cache-dir /tmp`, which would lead to the execution of: `restic --json --repo=sftp://example.com --cache-dir /tmp --password-file=None check`. Please note that this example should mainly highlight the problem in general. To prevent the problem, there is either escaping or again array-syntax. Escaping would use `shlex.quote` to place the user provided argument inside quotes and which also escapes everything which needs to be escaped. Using array syntax would mean providing the full command as an array like `['restic', '--json', '--repo', 'sftp://example.com']`. The array can then be given as-is to `Popen`. With this method, the proposed `shell_exec_with_user_input` would accept an array of array of strings.

### Patches

The fix follows the array-syntax approach proposed above:

* `linuxfabrik-lib` 5.0.0: `lib.shell.shell_exec()` requires the command as a list of
  arguments (argv) and always runs with `shell=False`. The `|` split functionality, command
  strings and the `shell=` parameter have been removed, so user-provided input can no longer
  break out of a command. `lib.shell.safe_cli_value()` additionally guards positional
  arguments (such as an ssh destination or a ping target) against option injection, and
  `lib.ssh` builds argument lists as well.
* Linuxfabrik Monitoring Plugins: all plugins assemble their external commands as argv lists
  (commit 23bb570f4). Contained in every release after v5.2.0.

## References
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-798h-hpph-m24j
- https://github.com/Linuxfabrik/monitoring-plugins
