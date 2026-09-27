# [H] asyncssh has SCP Path Traversal to Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-2wxc-x7rj-hg8f
CVE: CVE-2026-54591
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-2wxc-x7rj-hg8f
Type: github-advisory

## Affected
- PyPI: `asyncssh` — affected >=0 <2.23.1

## Details
| | |
|---|---|
| Product | asyncssh (all versions through 2.23.0) |
| Related | CVE-2019-6111 (same class in OpenSSH) |
| Fix | AsyncSSH 2.23.1 |

A malicious SSH server can write arbitrary files on the asyncssh SCP client's filesystem by sending filenames containing `../` traversal sequences. The SCP receive path does not currently sanitize server-provided filenames. By chaining directory traversals via the `D` (directory) action, an attacker can escape any target directory and overwrite `~/.bashrc`, `~/.ssh/rc`, or `~/.ssh/authorized_keys`, achieving code execution. This is the same vulnerability class as CVE-2019-6111. The mitigation applied in OpenSSH does not appear to have been adopted in asyncssh.

---

**Steps to exploit:**

**Step 1 - Normal usage:** Application calls `await asyncssh.scp((conn, 'file'), '/home/user/downloads/')`. This is the standard, documented API.

**Step 2 - SCP protocol:** asyncssh opens an SSH exec channel, runs `scp -f file`. The server controls the filename field:

```
C0644 100 ../pwned.txt\n       (simple traversal)

D0755 0 ..\n                   (traverse up, repeat as needed)
C0644 47 .bashrc\n             (write payload)
E\n
```

**Step 3 - `_parse_cd_args`** (`scp.py:134-142`) returns the filename verbatim:

```python
def _parse_cd_args(args: bytes) -> Tuple[int, int, bytes]:
    permissions, size, name = args.split(None, 2)
    return int(permissions, 8), int(size), name  # no sanitization
```

The returned `name` is not passed through `basename()` and is not checked for `..` or `/` components.

**Step 4 - `_recv_files`** (`scp.py:706-713`) joins the unsanitized name:

```python
new_dstpath = posixpath.join(dstpath, name)
```

With `dstpath=b'/home/user/downloads/subdir'` and `name=b'../pwned.txt'`, this resolves to `/home/user/downloads/pwned.txt`, outside the target.

**Step 5 - File write:** `_recv_file` opens the traversed path via `self._fs.open(dstpath, 'wb')` and writes attacker-controlled content. The resolved path is not checked against the target directory boundary.

**Step 6 - RCE chains:**

| Target | Execution trigger | Reliability |
|---|---|---|
| `~/.bashrc` | Next terminal open | High |
| `~/.profile` | Next login | High |
| `~/.ssh/rc` | Next SSH connection (requires sshd) | High |
| `~/.ssh/authorized_keys` | Attacker logs in with `command=` | Medium |

---

**Reproduction:**

Link to reproduction script: [path_traversal_poc.zip](https://github.com/user-attachments/files/28160665/path_traversal_poc.zip)

```bash
docker build -t asyncssh-scp-traversal -f Dockerfile .
docker run --rm asyncssh-scp-traversal
```

The attached `poc_scp_traversal.py` starts a malicious SSH server in-process using asyncssh's own API, then downloads from it via `asyncssh.scp()`.

*Expected Output:*

<img width="1400" height="815" alt="image" src="https://github.com/user-attachments/assets/496745e4-d11d-4ed8-bddd-d15dd13d1751" />

## References
- https://github.com/ronf/asyncssh/security/advisories/GHSA-2wxc-x7rj-hg8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-54591
- https://github.com/ronf/asyncssh/commit/d730803b8e4e94c20c7580d90f94d1e05f9f58de
- https://github.com/ronf/asyncssh
- https://github.com/ronf/asyncssh/releases/tag/v2.23.1
