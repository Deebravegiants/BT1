# [H] FoodCoopShop Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-jhww-fx2j-3rf7
CVE: CVE-2023-46725
CWE: CWE-367, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-11-02
Source: https://github.com/advisories/GHSA-jhww-fx2j-3rf7
Type: github-advisory

## Affected
- Packagist: `foodcoopshop/foodcoopshop` — affected >=3.2.0 <3.6.1

## Details
There is a potential SSRF vulnerability in foodcoopshop. Since there is no security policy on your Github, I tried to use the emails to contact you.

The potential issue is in the Network module, where a manufacturer account can use the /api/updateProducts.json endpoint to make the server send a request to arbitrary host.
For example, use
```
data[data][0][remoteProductId]=352&data[data][0][image]=http://localhost:8888/
```
will make the server send a request to localhost:8888. This means that it can be used as a proxy into the internal network where the server is.

To make matters worse, the checks on valid image is not enough. There is time of check time of use issue there.
For example, by using a custom server that returns 200 on HEAD requests, then return a valid image on first GET request and then a 302 redirect to final target on second GET request, the server will copy whatever file
at the redirect destination, making this a full SSRF.
(An example python server that can do this is at https://pastebin.com/8K5Brwbq This will make the server download whatever at the redirect target)

You can check https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html for more information on SSRF, their impact and how to properly fix it.

Regards

## References
- https://github.com/foodcoopshop/foodcoopshop/security/advisories/GHSA-jhww-fx2j-3rf7
- https://nvd.nist.gov/vuln/detail/CVE-2023-46725
- https://github.com/foodcoopshop/foodcoopshop/pull/972
- https://github.com/foodcoopshop/foodcoopshop/commit/0d5bec5c4c22e1affe7fd321a30e3f3a4d99e808
- https://github.com/foodcoopshop/foodcoopshop
- https://pastebin.com/8K5Brwbq
