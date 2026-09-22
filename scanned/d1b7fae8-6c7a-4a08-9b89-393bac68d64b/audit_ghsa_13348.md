# [H] Feathers socket handler allows abusing implicit toString

## Summary
Severity: High
Advisory: GHSA-hhr9-rh25-hvf9
CVE: CVE-2023-37899
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-hhr9-rh25-hvf9
Type: github-advisory

## Affected
- npm: `@feathersjs/socketio` — affected >=0 <4.5.18
- npm: `@feathersjs/socketio` — affected >=5.0.0 <5.0.8
- npm: `@feathersjs/transport-commons` — affected >=0 <4.5.18
- npm: `@feathersjs/transport-commons` — affected >=5.0.0 <5.0.8

## Details
### Impact

Feathers socket handler did not catch invalid string conversion errors like:

```ts
const message = `${{ toString: '' }}`
```

Causing the NodeJS process to crash when sending an unexpected Socket.io message like

```ts
socket.emit('find', { toString: '' })
```

### Patches

A fix has been released in

- `v5.0.8` via #3241
- `v4.5.18` via #3242

### Workarounds

Since it is in the core Socket handling code upgrading to the latest version is necessary.
### References

- [v5.0.8 Changelog](https://github.com/feathersjs/feathers/blob/dove/CHANGELOG.md#508-2023-07-19)
- [v4.5.18 Changelog](https://github.com/feathersjs/feathers/blob/crow/CHANGELOG.md#4518-2023-07-19)

## References
- https://github.com/feathersjs/feathers/security/advisories/GHSA-hhr9-rh25-hvf9
- https://nvd.nist.gov/vuln/detail/CVE-2023-37899
- https://github.com/feathersjs/feathers/pull/3241
- https://github.com/feathersjs/feathers/pull/3242
- https://github.com/feathersjs/feathers/commit/0b9a6b19b12ad05934e4c8bd9917448ed39d1ed8
- https://github.com/feathersjs/feathers/commit/c397ab3a0cd184044ae4f73540549b30a396821c
- https://github.com/feathersjs/feathers
- https://github.com/feathersjs/feathers/blob/crow/CHANGELOG.md#4518-2023-07-19
- https://github.com/feathersjs/feathers/blob/dove/CHANGELOG.md#508-2023-07-19
