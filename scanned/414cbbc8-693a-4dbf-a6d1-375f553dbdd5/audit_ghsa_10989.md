# [M] TinaCMS CLI has Arbitrary File Read via Disabled Vite Filesystem Restriction

## Summary
Severity: Medium
Advisory: GHSA-m48g-4wr2-j2h6
CVE: CVE-2026-29066
CWE: CWE-200, CWE-552
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-m48g-4wr2-j2h6
Type: github-advisory

## Affected
- npm: `@tinacms/cli` — affected >=0 <2.1.8

## Details
## Summary
The TinaCMS CLI dev server configures Vite with `server.fs.strict: false`, which disables Vite's built-in filesystem access restriction. This allows any unauthenticated attacker who can reach the dev server to read arbitrary files on the host system

## Details
When running `tinacms dev`, the CLI starts a Vite dev server configured in:
`packages/@tinacms/cli/src/next/vite/index.ts`
```
server: {
  host: configManager.config?.build?.host ?? false,
  ...
  fs: {
    strict: false, // Disables Vite's filesystem access restriction
  },
},
```
TinaCMS middleware only intercepts specific route prefixes (/media/*, /graphql, /altair, /searchIndex). Any request to a path outside these routes falls through to Vite's default static file handler, which will serve the file directly from the absolute path on the filesystem.
Additionally, the server enables permissive CORS (cors() with no origin restriction), which may further facilitate browser-based exploitation such as DNS rebinding attacks.

## PoC

**Prerequisites**: TinaCMS CLI dev server running (default port 4001).

- Read system files directly:
```
curl http://localhost:4001/etc/passwd
```
<img width="705" height="332" alt="image" src="https://github.com/user-attachments/assets/6fd0e1c7-a549-40c8-bc81-af9c343f52a0" />

```
curl http://localhost:4001/etc/hostname
```
<img width="631" height="41" alt="image" src="https://github.com/user-attachments/assets/bd103dc3-d4c3-4774-8007-b55de3fc2a9e" />
Vite resolves and serves the absolute path directly from the filesystem.


## Impact
Any developer running tinacms dev in an environment where the dev server port is reachable by an attacker. This includes:

- Cloud IDEs (GitHub Codespaces, Gitpod) where ports are automatically forwarded and publicly accessible

- Docker or VM setups with port forwarding configured

- Misconfigured environments binding to 0.0.0.0 via the build.host config option

- Systems targeted via DNS rebinding attacks, leveraging the unrestricted CORS policy

- Local environments with malicious dependencies running on the same machine

An attacker who can reach port 4001 can:

- Read any file readable by the server process (/etc/passwd, /etc/shadow, SSH private keys)

- Exfiltrate environment variables and secrets via /proc/self/environ

- Access cloud credentials and API keys from configuration files

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-m48g-4wr2-j2h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-29066
- https://github.com/tinacms/tinacms
