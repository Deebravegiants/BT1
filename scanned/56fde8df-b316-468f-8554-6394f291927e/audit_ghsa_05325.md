# [H] Budibase: Unauthenticated S3 signed upload URL generation allows arbitrary writes with stored datasource credentials

## Summary
Severity: High
Advisory: GHSA-jj36-r9w3-3pfh
CVE: CVE-2026-50136
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-jj36-r9w3-3pfh
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.2

## Details
The application server exposes an unauthenticated endpoint that generates S3 `PutObject` presigned URLs using credentials stored in a workspace datasource. The route is protected only by the recaptcha middleware and does not require authentication, table permission, datasource permission, or builder access. A public caller who knows a workspace ID and S3 datasource ID can request a signed upload URL for attacker-controlled bucket and key values.

### Details

The static route registers the signed upload URL endpoint with only `recaptcha` before the controller:

- `packages/server/src/api/routes/static.ts:44-48`

```ts
44:  .post(
45:    "/api/attachments/:datasourceId/url",
46:    recaptcha,
47:    controller.getSignedUploadURL
48:  )
```

The controller loads the datasource by `datasourceId` with enriched secret values:

- `packages/server/src/api/controllers/static/index.ts:590-598`

```ts
590:export const getSignedUploadURL = async function (
591:  ctx: Ctx<GetSignedUploadUrlRequest, GetSignedUploadUrlResponse>
592:) {
593:  // Ensure datasource is valid
594:  let datasource
595:  try {
596:    const { datasourceId } = ctx.params
597:    datasource = await sdk.datasources.get(datasourceId, { enriched: true })
598:    if (!datasource) {
```

The request body controls `bucket` and `key`, and the server signs a PUT URL using the stored datasource credentials:

- `packages/server/src/api/controllers/static/index.ts:609-629`

```ts
609:  if (datasource?.source === "S3") {
610:    const { bucket, key } = ctx.request.body || {}
611:    if (!bucket || !key) {
612:      ctx.throw(400, "bucket and key values are required")
613:    }
614:    try {
615:      let endpoint = datasource?.config?.endpoint
616:      if (endpoint && !utils.urlHasProtocol(endpoint)) {
617:        endpoint = `https://${endpoint}`
618:      }
619:      const s3 = new S3({
620:        region: awsRegion,
621:        endpoint: endpoint,
622:        credentials: {
623:          accessKeyId: datasource?.config?.accessKeyId as string,
624:          secretAccessKey: datasource?.config?.secretAccessKey as string,
625:        },
626:      })
627:      const params = { Bucket: bucket, Key: key }
628:      signedUrl = await getSignedUrl(s3, new PutObjectCommand(params))
629:      if (endpoint) {
```

The endpoint returns the signed URL and public URL to the caller:

- `packages/server/src/api/controllers/static/index.ts:630-639`

```ts
630:        publicUrl = `${endpoint}/${bucket}/${key}`
631:      } else {
632:        publicUrl = `https://${bucket}.s3.${awsRegion}.amazonaws.com/${key}`
633:      }
634:    } catch (error: any) {
635:      ctx.throw(400, error)
636:    }
637:  }
638:
639:  ctx.body = { signedUrl, publicUrl }
```

Because no authorization middleware is applied, the API trusts public input to choose where the stored S3 credentials will write.

### PoC

Non-destructive validation approach:

1. Create or identify a workspace with an S3 datasource.
2. Obtain the production workspace ID and S3 datasource ID.
3. Send an unauthenticated request with the workspace ID header and attacker-controlled bucket/key:

```http
POST /api/attachments/<datasourceId>/url HTTP/1.1
x-budibase-app-id: app_<workspace-id>
content-type: application/json

{"bucket":"attacker-controlled-or-permitted-bucket","key":"poc/budibase.txt"}
```

4. Observe that the response contains a signed PUT URL.
5. Upload harmless content to the returned `signedUrl` and confirm the object is created using the datasource's stored S3 credentials.

### Impact

This allows unauthenticated arbitrary object writes wherever the stored S3 datasource credentials have `PutObject` access. Depending on the datasource permissions, this can corrupt application data, overwrite public assets, place attacker-controlled objects in trusted buckets, consume storage, or abuse an organization's cloud credentials.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-jj36-r9w3-3pfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-50136
- https://github.com/Budibase/budibase/pull/18774
- https://github.com/Budibase/budibase/commit/d9dbb7f6105373cc88ecacdbcab70c776f7dd6a1
- https://github.com/Budibase/budibase
