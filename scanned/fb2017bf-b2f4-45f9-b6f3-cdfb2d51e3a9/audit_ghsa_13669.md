# [M] Uptime Kuma Authenticated remote code execution via TailscalePing

## Summary
Severity: Medium
Advisory: GHSA-hfxh-rjv7-2369
Ecosystem: npm
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-hfxh-rjv7-2369
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=1.23.0 <1.23.7

## Details
### Summary

The `runTailscalePing` method of the `TailscalePing` class injects the `hostname` parameter inside a shell command, leading to a command injection and the possibility to run arbitrary commands on the server.

### Details

When adding a new monitor on Uptime Kuma, we can select the "Tailscale Ping" type. Then we can add a hostname and insert a command injection payload into it. The front-end application requires that the field follow a specific pattern, this validation only happens on the front-end and can be removed by removing the attribute `pattern` on the `input` element.

https://github.com/louislam/uptime-kuma/blob/dc4242019331e65a79ac16deef97510144e01b12/server/monitor-types/tailscale-ping.js#L40-L46

We can finally add the new monitor and observe that our command is being executed.

**NOTE:** When using Uptime Kuma inside a container, the "TailScale Ping" type is not visible. We can fake this information by intercepting WebSocket messages and set the `isContainer` option to `false`.

### PoC

* Authenticate.
* Create a new monitor.
* Select the TailScale Ping type (if not visible, see the note in the details section).
* Insert the command injection payload inside the `hostname` field. (for example `$(id >&2)`)
* Remove the `pattern` requirement on the field.
* Save and start the monitor.

### Impact

An authenticated user can execute arbitrary command on the server running Uptime Kuma.

### Remediation

There are other command execution in the codebase, they use a method `spawn` from the `child_process` module which does not interpret the command as a shell command, the same thing should be done here.

**NOTE:** The Tailscale CLI seems to support the `--` sequence. It should be used between the `ping` subcommand and the `hostname` argument to avoid argument injection.

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-hfxh-rjv7-2369
- https://github.com/louislam/uptime-kuma
