# [C] Signal K set-system-time plugin vulnerable to RCE - Command Injection

## Summary
Severity: Critical
Advisory: GHSA-p8gp-2w28-mhwg
CVE: CVE-2026-23515
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-p8gp-2w28-mhwg
Type: github-advisory

## Affected
- npm: `@signalk/set-system-time` — affected >=0 <1.5.0

## Details
### Summary
A Command Injection vulnerability allows authenticated users with write permissions to execute arbitrary shell commands on the Signal K server when the set-system-time plugin is enabled. Unauthenticated users can also exploit this vulnerability if security is disabled on the Signal K server. This occurs due to unsafe construction of shell commands when processing `navigation.datetime` values received via WebSocket delta messages.

### Details
**Product:** Signal K set-system-time plugin  
**Repository:** https://github.com/SignalK/set-system-time  

File: `index.js`, lines 60-71

```javascript
      stream.onValue(function (datetime) {
        var child
        if (process.platform == 'win32') {
          console.error("Set-system-time supports only linux-like os's")
        } else {
          if( ! plugin.useNetworkTime(options) ){
            const useSudo = typeof options.sudo === 'undefined' || options.sudo
            const setDate = `date --iso-8601 -u -s "${datetime}"`  // ← VULNERABLE
            const command = useSudo
              ? `if sudo -n date &> /dev/null ; then sudo ${setDate} ; else exit 3 ; fi`
              : setDate
            child = require('child_process').spawn('sh', ['-c', command])  // ← EXECUTES SHELL
```

The vulnerability has three components:

1. **Unsanitized Input**: The `datetime` value from `navigation.datetime` Signal K path is directly interpolated into a shell command without validation
2. **Shell Execution**: The command is executed via `spawn('sh', ['-c', command])`, which interprets shell metacharacters
3. **Sudo Privileges**: The plugin can execute with root privileges if `sudo` is misconfigured, instructions to limit passwordless sudo to the /bin/date binary helps mitigate this but RCE can still be achieved with the privileges of the user that installed it.

### PoC
#### Exploitation Requirements

- Signal K server with security enabled, if disabled credentials not required
- Valid user credentials with `readwrite` or `admin` permissions
- set-system-time plugin installed and enabled
- Signal K server installed on a Linux OS
- Passwordless sudo configured, official instructions will do this for the `date` command which is enough to satisfy the if condition


```Python
"""
Run provided POC:
    python3 poc.py --host signalkserver_IP -u username -p password

Payload: Creates /tmp/signalk-RCE.txt to prove code execution
"""
```

### Impact
An attacker that has write privileges either through security on the Signal K server being disabled or valid credentials with read/write permissions can execute arbitrary commands on the server with the privileges of the SignalK process or root if sudo is misconfigured. This enables complete system compromise.

### Recommendations

- Replace shell-based execution with child_process.execFile() so user-controlled input is passed as arguments rather than interpreted by a shell.

- Validate that navigation.datetime conforms to an expected ISO-8601 format to improve robustness.

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-p8gp-2w28-mhwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-23515
- https://github.com/SignalK/set-system-time/commit/75b11eae2de528bf89ede3fb1f7ed057ddbb4d24
- https://github.com/SignalK/signalk-server
