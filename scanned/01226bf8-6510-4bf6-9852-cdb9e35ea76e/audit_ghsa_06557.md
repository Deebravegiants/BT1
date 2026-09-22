# [H] Pterodactyl's improper JWT scoping allows subuser to upload files when not explicitly granted `file.create` permissions

## Summary
Severity: High
Advisory: GHSA-8r6w-3qq5-4p4r
CVE: CVE-2026-54593
CWE: CWE-1259, CWE-1270
Ecosystem: Go, Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-8r6w-3qq5-4p4r
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.3
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.12.2

## Details
### Summary
A privilege escalation vulnerability exists in the Wings /upload/file endpoint due to insufficient validation of panel-signed JWTs. Wings accepts any valid panel-signed JWT containing `server_uuid`, `user_uuid`, and `unique_id`, regardless of the token’s intended purpose. Because the Panel issues JWTs with these same claims for other lower-privilege operations (such as WebSocket authentication and file download links), an authenticated subuser can reuse one of those tokens to upload arbitrary files without possessing the required `file.create` permission.

### Impact
Any subuser with permission to connect to a server's console, download files, or download backups could reuse those tokens to upload arbitrary files to the _same server_. A user that does not have access to a server as a subuser is not able to arbitrarily upload files.

### Details
The panel generated JWT tokens for various purposes:
- https://github.com/pterodactyl/panel/blob/0f82c105201b192d229f6abd5827e2ee7e672a05/app/Services/Backups/DownloadLinkService.php#L33-L36
- https://github.com/pterodactyl/panel/blob/0f82c105201b192d229f6abd5827e2ee7e672a05/app/Http/Controllers/Api/Client/Servers/FileUploadController.php#L45
- https://github.com/pterodactyl/panel/blob/0f82c105201b192d229f6abd5827e2ee7e672a05/app/Http/Controllers/Api/Client/Servers/WebsocketController.php#L58-L61
- https://github.com/pterodactyl/panel/blob/0f82c105201b192d229f6abd5827e2ee7e672a05/app/Http/Controllers/Api/Client/Servers/FileController.php#L82-L85
Though as the actual purpose is not conveyed part of the JWT tokens, this introduces this vulnerability of being able to do non-intended actions due to the expected fields (i.e. `server_uuid`) on most endpoints being the same when parsing it on wings' side.  

### PoC
Create a new subuser that has the minimal amount of permissions on a server (`websocket.connect`). As that subuser, retrieve a websocket JWT token from the `GET /api/client/servers/[...]/websocket` endpoint (in my case, I manually just make a request under that user's browser session; you can probably just resend the /websocket request in browser console to get a fresh unused token). Using that websocket token, we can abuse this by directly using it in the `/upload/file` endpoint of the wings node instead of using it for websocket authentication:
```python3
import requests

wings_url = 'http://[...]:8080'
websocket_token = '[...]'

res = requests.post(f'{wings_url}/upload/file', params = {
    'token': websocket_token,
}, files = {
    'files': ('file-upload.txt', b'Hello, World!'),
})
print(res.status_code, res.content)
```
Observe, that even though our subuser never has permissions outside viewing the console, they are able to write arbitrary files in the server. This pattern happens in a lot of other action, but this is probably the most interesting one.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-8r6w-3qq5-4p4r
- https://github.com/pterodactyl/panel/pull/5636
- https://github.com/pterodactyl/panel/commit/7ffcd636310bb72b54bac3280d2a15e727feded7
- https://github.com/pterodactyl/wings/commit/d0ddc80844479302abdaf9654de3bacd511c0f5c
- https://github.com/pterodactyl/panel
