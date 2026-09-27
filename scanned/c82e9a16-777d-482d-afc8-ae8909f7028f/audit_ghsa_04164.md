# [M] pnpm: Tarball hash of GitHub git dependencies is not stored in lockfile

## Summary
Severity: Medium
Advisory: GHSA-hg3w-7f8c-63hp
CVE: CVE-2026-48995
CWE: CWE-353
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-hg3w-7f8c-63hp
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.33.4
- npm: `pnpm` — affected >=11.0.0 <11.0.7

## Details
### Summary

A malicious `codeload.github.com` server can serve whatever tarball it wants and pnpm will install it regardless of the lockfile.

### Details

The lockfile does not store the hash of the dependencies from https://codeload.github.com

This means that if this server was compromised or a person's machine configuration was compromised, pnpm would download and install these dependencies.

### PoC

```sh
> pnpm -v     
10.28.2
```

Given the following package.json:

```json
{
  "dependencies": {
    "add": "git://github.com/dsherret/npm-git-dep.git#b3eeb9b"
  }
}
```

This produces a lockfile like so:

```yaml
lockfileVersion: '9.0'

settings:
  autoInstallPeers: true
  excludeLinksFromLockfile: false

importers:

  .:
    dependencies:
      add:
        specifier: git://github.com/dsherret/npm-git-dep.git#b3eeb9b
        version: https://codeload.github.com/dsherret/npm-git-dep/tar.gz/b3eeb9b

packages:

  add@https://codeload.github.com/dsherret/npm-git-dep/tar.gz/b3eeb9b:
    resolution: {tarball: https://codeload.github.com/dsherret/npm-git-dep/tar.gz/b3eeb9b}
    version: 1.0.0

snapshots:

  add@https://codeload.github.com/dsherret/npm-git-dep/tar.gz/b3eeb9b: {}
```

Notice that there is no hash. The `b3eeb9b` is not sufficient because I can configure my machine to resolve a compromised tarball from that url (I tested it out and pnpm just installs it).

### Impact

Anyone relying on github git dependencies.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-hg3w-7f8c-63hp
- https://nvd.nist.gov/vuln/detail/CVE-2026-48995
- https://github.com/pnpm/pnpm
