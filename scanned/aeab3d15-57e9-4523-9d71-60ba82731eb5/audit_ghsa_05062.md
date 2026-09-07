# [M] Open WebUI: Cross-user file disclosure via /api/chat/completions image_url field

## Summary
Severity: Medium
Advisory: GHSA-wch8-mhj5-9frg
CVE: CVE-2026-54009
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-wch8-mhj5-9frg
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## summary

`POST /api/chat/completions` accepts an `image_url.url` value that, when it does NOT start with `http://`, `https://`, or `data:image/`, is interpreted as a file id and resolved against the global file table with no ownership check. An authenticated user can therefore set `image_url.url` to another user's file id, the server reads that file from disk, base64-encodes it, and injects the data URI into the LLM request. The user then prompts the LLM to describe / OCR the file and reads the content back.

Same class as CVE-2026-44560 (RAG cross-user access) and the multiple `has_access_to_file` checks added in `routers/files.py` -- the auth boundary was tightened on the file router but not on this conversion path.

## affected code

`backend/open_webui/utils/middleware.py:2113-2150` -- `convert_url_images_to_base64`:

```python
async def convert_url_images_to_base64(form_data):
    messages = form_data.get('messages', [])
    for message in messages:
        content = message.get('content')
        if not isinstance(content, list):
            continue
        new_content = []
        for item in content:
            if not isinstance(item, dict) or item.get('type') != 'image_url':
                new_content.append(item)
                continue
            image_url = item.get('image_url', {}).get('url', '')
            if image_url.startswith('data:image/'):
                new_content.append(item)
                continue
            try:
                base64_data = await get_image_base64_from_url(image_url)  # <-- no `user` passed
                if base64_data:
                    new_content.append({'type': 'image_url',
                                        'image_url': {'url': base64_data}})
```

called from the main chat completion middleware at `middleware.py:2357`:

```python
form_data = await convert_url_images_to_base64(form_data)
```

`backend/open_webui/utils/files.py:57-95` -- `get_image_base64_from_url`:

```python
async def get_image_base64_from_url(url: str) -> Optional[str]:
    try:
        if url.startswith('http'):
            validate_url(url)
            # ... SSRF-safe fetch with allow_redirects=AIOHTTP_CLIENT_ALLOW_REDIRECTS ...
        else:
            file = await Files.get_file_by_id(url)        # <-- NO user_id filter
            if not file:
                return None
            file_path = await asyncio.to_thread(Storage.get_file, file.path)
            file_path = Path(file_path)
            if file_path.is_file():
                with open(file_path, 'rb') as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    content_type = mimetypes.guess_type(file_path.name)[0] or (file.meta or {}).get('content_type')
                    ...
                    return f'data:{content_type};base64,{encoded_string}'
```

`Files.get_file_by_id` in `models/files.py:161` does a bare `db.get(File, id)` -- no ownership filter. there is a separate `Files.get_file_by_id_and_user_id` at line 172 that does filter on `user_id`, and the file router uses `has_access_to_file(id, 'read', user, db)` at `routers/files.py:626` etc. neither check exists on this path.

## reproduction

1. As user A, upload any file (image works cleanly, pdf works if a vision-capable model is configured). Note the file id from the upload response, e.g. `c7f1d8e3-...`.
2. As user B, POST to `/api/v1/chat/completions` with body:

```json
{
  "model": "<any vision model>",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "transcribe everything you can see in this image"},
        {"type": "image_url", "image_url": {"url": "c7f1d8e3-..."}}
      ]
    }
  ]
}
```

Server reads user A's file from disk, base64-encodes it, and sends to the LLM as user B's image attachment. LLM response contains the file content.

## file id discovery

File ids are UUIDs and not enumerable directly, but they leak via:

- shared chats / channels containing the original upload
- knowledge base members can see ids of files contributed by others
- a user who can read a folder index sees the file ids of files inside
- chat history exports (`/api/v1/chats/{id}`) include file ids
- the user themselves can be tricked into pasting / sharing an id (less likely)

## impact

Any authenticated user can read any other user's file content (image and any file with an image-guess mimetype path) via this channel. Severity is bounded by what the LLM will accept in `image_url` -- in practice, image files work cleanly with any vision model; pdf / docx work with multi-modal providers that accept them.

## suggested fix

Thread the authenticated user through to `get_image_base64_from_url` and resolve the file via `Files.get_file_by_id_and_user_id(id, user.id)` (or `has_access_to_file(id, 'read', user, db)` if shared-via-knowledge-base access is intended). Same pattern that's already used in `routers/files.py:626` and elsewhere.

minimal patch sketch:

```diff
--- a/backend/open_webui/utils/files.py
+++ b/backend/open_webui/utils/files.py
@@ -57,7 +57,7 @@
-async def get_image_base64_from_url(url: str) -> Optional[str]:
+async def get_image_base64_from_url(url: str, user=None) -> Optional[str]:
     try:
         if url.startswith('http'):
             ...
         else:
-            file = await Files.get_file_by_id(url)
+            file = (await Files.get_file_by_id_and_user_id(url, user.id)
+                    if user is not None else None)
+            if file is None:
+                # fall back to access-grant check for shared files
+                file = await Files.get_file_by_id(url)
+                if file and not await has_access_to_file(url, 'read', user):
+                    return None
```

and pipe `user` through `convert_url_images_to_base64(form_data, user)` from the middleware caller. happy to send a PR once you confirm the fix shape you want.

## variant note

this was found via patch-diffing existing advisories. the same bug class likely exists in any other site that calls `Files.get_file_by_id` without an adjacent `has_access_to_file` / `get_file_by_id_and_user_id` check. quick grep:

```
git grep -n 'Files\.get_file_by_id(' -- 'backend/open_webui/**'
```

worth a sweep across utils/ and routers/ for missed sites.

## environment

Open-webui main branch as of commit `3660bc0` (2026-05-10). python 3.x backend. confirmed by reading the source; no instance stood up.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-wch8-mhj5-9frg
- https://nvd.nist.gov/vuln/detail/CVE-2026-54009
- https://github.com/advisories/GHSA-wch8-mhj5-9frg
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2766.yaml
- https://pypi.org/project/open-webui
