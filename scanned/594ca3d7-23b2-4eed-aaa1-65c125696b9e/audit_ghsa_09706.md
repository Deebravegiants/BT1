# [C] RClone: Unauthenticated operations/fsinfo allows attacker-controlled backend instantiation and local command execution

## Summary
Severity: Critical
Advisory: GHSA-jfwf-28xr-xw6q
CVE: CVE-2026-41179
CWE: CWE-306, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-jfwf-28xr-xw6q
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=1.48.0 <1.73.5

## Details
### Summary
The RC endpoint `operations/fsinfo` is exposed without `AuthRequired: true` and accepts attacker-controlled `fs` input. Because `rc.GetFs(...)` supports inline backend definitions, an unauthenticated attacker can instantiate an attacker-controlled backend on demand. For the WebDAV backend, `bearer_token_command` is executed during backend initialization, making single-request unauthenticated local command execution possible on reachable RC deployments without global HTTP authentication.

### Preconditions

Preconditions for this vulnerability are:

- The rclone remote control API **must** be enabled, either by the `--rc` flag or by running the `rclone rcd` server
- The remote control API **must** be reachable by the attacker - by default rclone only serves the rc to localhost unless the `--rc-addr` flag is in use
- The rc must have been deployed **without** global RC HTTP authentication - so not using `--rc-user`/`--rc-pass`/`--rc-htpasswd`/etc


### Details
The root cause consists of the following pieces:

1. `operations/fsinfo` is not protected with `AuthRequired: true`
2. `operations/fsinfo` calls `rc.GetFs(...)` on attacker-controlled input
3. `rc.GetFs(...)` supports inline backend creation through object-valued `fs`
4. WebDAV backend initialization executes `bearer_token_command`

Relevant code paths:

- [`fs/operations/rc.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/operations/rc.go)
  - `operations/fsinfo` is registered without `AuthRequired: true`
  - `rcFsInfo()` calls `rc.GetFs(ctx, in)`

- [`fs/rc/cache.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/rc/cache.go)
  - `GetFs()` / `GetFsNamed()` can parse an object-valued `fs`
  - `getConfigMap()` converts attacker-controlled JSON into a backend config string

- [`backend/webdav/webdav.go`](https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/backend/webdav/webdav.go)
  - `bearer_token_command` is a supported backend option
  - `NewFs(...)` calls `fetchAndSetBearerToken()` when `bearer_token_command` is set
  - `fetchBearerToken()` invokes `exec.Command(...)`

This creates a practical single-request unauthenticated command-execution primitive on reachable RC servers without global HTTP authentication.

This was alidated on:
- current `master` as of 2026-04-14: `bf55d5e6d37fd86164a87782191f9e1ffcaafa82`
- latest public release tested locally: `v1.73.4`

This was also validated on a public amd64 Ubuntu host controlled by the tester, using direct host execution (not containerized PoC execution).

### PoC
#### Minimal single-request form PoC
Start a vulnerable RC server:

```bash
rclone rcd --rc-addr 127.0.0.1:5572
```

No `--rc-user`, no `--rc-pass`, no `--rc-htpasswd`.

Then send a single request:

```bash
curl -sS -X POST http://127.0.0.1:5572/operations/fsinfo \
  --data-urlencode "fs=:webdav,url='http://127.0.0.1/',vendor=other,bearer_token_command='/usr/bin/touch /tmp/rclone_fsinfo_rce_poc_marker':"
```

Expected result:
- HTTP 200 JSON response from `operations/fsinfo`
- `/tmp/rclone_fsinfo_rce_poc_marker` is created on the host

### Impact
This is effectively a single-request unauthenticated command-execution vulnerability on reachable RC deployments without global HTTP authentication.

In practice, command execution in the rclone process context can lead to higher-impact outcomes such as local file read, file write, or shell access, depending on the deployed environment.

#### Testing performed
This was successfully reproduced:
- on a local test environment
- on a public amd64 Ubuntu host controlled by the tester

On the public host it was confirmed:

- the unauthenticated `operations/fsinfo` exploit worked
- command execution occurred on the host
- the issue was reproducible through direct host execution

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-jfwf-28xr-xw6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41179
- https://github.com/rclone/rclone/commit/2a9e952b38e03a96bf40c9eb6e8e22199865ee3b
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/backend/webdav/webdav.go
- https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/operations/rc.go
- https://github.com/rclone/rclone/blob/bf55d5e6d37fd86164a87782191f9e1ffcaafa82/fs/rc/cache.go
- https://github.com/rclone/rclone/releases/tag/v1.73.5
- https://rclone.org/changelog/#v1-73-5-2026-04-19
