# [H] React Router allows pre-render data spoofing on React-Router framework mode

## Summary
Severity: High
Advisory: GHSA-cpj6-fhp6-mr6j
CVE: CVE-2025-43865
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-04-24
Source: https://github.com/advisories/GHSA-cpj6-fhp6-mr6j
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0-pre.0 <7.5.2

## Details
## Summary
After some research, it turns out that it's possible to modify pre-rendered data by adding a header to the request. This allows to completely spoof its contents and modify all the values ​​of the data object passed to the HTML. Latest versions are impacted.

## Details
The vulnerable header is `X-React-Router-Prerender-Data`, a specific JSON object must be passed to it in order for the spoofing to be successful as we will see shortly. Here is [the vulnerable code](https://github.com/remix-run/react-router/blob/e6c53a0130559b4a9bd47f9cf76ea5b08a69868a/packages/react-router/lib/server-runtime/routes.ts#L87) :

<img width="776" alt="Capture d’écran 2025-04-07 à 05 36 58" src="https://github.com/user-attachments/assets/c95b0b33-15ce-4d30-9f5e-b10525dd6ab4" />

To use the header, React-router must be used in Framework mode, and for the attack to be possible the target page must use a loader.

## Steps to reproduce 
Versions used for our PoC: 
- "@react-router/node": "^7.5.0",
- "@react-router/serve": "^7.5.0",
- "react": "^19.0.0"
- "react-dom": "^19.0.0"
- "react-router": "^7.5.0"

1. Install React-Router with its default configuration in Framework mode (https://reactrouter.com/start/framework/installation)
2. Add a simple page using a loader (example: `routes/ssr`)
3. Access your page (*which uses the loader*) by suffixing it with `.data`. In our case the page is called `/ssr`:

![image](https://github.com/user-attachments/assets/d7d04e86-c549-4f4a-9200-2d1b6ac96aad)

We access it by adding the suffix `.data` and retrieve the data object, needed for the header:

![image](https://github.com/user-attachments/assets/ea0ca23e-6ba5-49c1-980d-1b04a05acf56)

4. Send your request by adding the `X-React-Router-Prerender-Data` header with the previously retrieved object as its value. You can change any value of your `data` object (do not touch the other values, the latter being necessary for the object to be processed correctly and not throw an error):

![Capture d’écran 2025-04-07 à 05 56 10](https://github.com/user-attachments/assets/42ca7c9e-5cd3-4eff-9711-1e78755c9046)

As you can see, all values ​​have been changed/overwritten by the values ​​provided via the header. 

## Impact
The impact is significant, if a cache system is in place, it is possible to poison a response in which all of the data transmitted via a loader would be altered by an attacker allowing him to take control of the content of the page and modify it as he wishes via a cache-poisoning attack. This can lead to several types of attacks including potential stored XSS depending on the context in which the data is injected and/or how the data is used on the client-side.

## Credits
- Rachid Allam (zhero;)
- Yasser Allam (inzo_)

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-cpj6-fhp6-mr6j
- https://nvd.nist.gov/vuln/detail/CVE-2025-43865
- https://github.com/remix-run/react-router/commit/c84302972a152d851cf5dd859ff332b354b70111
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/e6c53a0130559b4a9bd47f9cf76ea5b08a69868a/packages/react-router/lib/server-runtime/routes.ts#L87
