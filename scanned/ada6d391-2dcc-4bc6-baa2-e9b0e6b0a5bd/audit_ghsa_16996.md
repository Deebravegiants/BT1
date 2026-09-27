# [M] Vite's `server.fs.deny` did not deny requests for patterns with directories.

## Summary
Severity: Medium
Advisory: GHSA-8jhw-289h-jh2g
CVE: CVE-2024-31207
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-03
Source: https://github.com/advisories/GHSA-8jhw-289h-jh2g
Type: github-advisory

## Affected
- npm: `vite` — affected >=2.7.0 <2.9.18
- npm: `vite` — affected >=3.0.0 <3.2.10
- npm: `vite` — affected >=4.0.0 <4.5.3
- npm: `vite` — affected >=5.0.0 <5.0.13
- npm: `vite` — affected >=5.1.0 <5.1.7
- npm: `vite` — affected >=5.2.0 <5.2.6

## Details
### Summary
[Vite dev server option](https://vitejs.dev/config/server-options.html#server-fs-deny) `server.fs.deny` did not deny requests for patterns with directories. An example of such a pattern is `/foo/**/*`.

### Impact
Only apps setting a custom `server.fs.deny` that includes a pattern with directories, and explicitly exposing the Vite dev server to the network (using `--host` or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host)) are affected.

### Patches
Fixed in vite@5.2.6, vite@5.1.7, vite@5.0.13, vite@4.5.3, vite@3.2.10, vite@2.9.18

### Details
`server.fs.deny` uses picomatch with the config of `{ matchBase: true }`. [matchBase](https://github.com/micromatch/picomatch/blob/master/README.md#options:~:text=Description-,basename,-boolean) only matches the basename of the file, not the path due to a bug (https://github.com/micromatch/picomatch/issues/89). The vite config docs read like you should be able to set fs.deny to glob with picomatch. Vite also does not set `{ dot: true }` and that causes [dotfiles not to be denied](https://github.com/micromatch/picomatch/blob/master/README.md#options:~:text=error%20is%20thrown.-,dot,-boolean) unless they are explicitly defined.

**Reproduction**

Set fs.deny to `['**/.git/**']` and then curl for `/.git/config`.

* with `matchBase: true`, you can get any file under  `.git/` (config, HEAD, etc).
* with `matchBase: false`, you cannot get any file under  `.git/` (config, HEAD, etc).

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-8jhw-289h-jh2g
- https://nvd.nist.gov/vuln/detail/CVE-2024-31207
- https://github.com/vitejs/vite/commit/011bbca350e447d1b499d242804ce62738c12bc0
- https://github.com/vitejs/vite/commit/5a056dd2fc80dbafed033062fe6aaf4717309f48
- https://github.com/vitejs/vite/commit/89c7c645f09d16a38f146ef4a1528f218e844d67
- https://github.com/vitejs/vite/commit/96a7f3a41ef2f9351c46f3ab12489bb4efa03cc9
- https://github.com/vitejs/vite/commit/ba5269cca81de3f5fbb0f49d58a1c55688043258
- https://github.com/vitejs/vite/commit/d2db33f7d4b96750b35370c70dd2c35ec3b9b649
- https://github.com/vitejs/vite
