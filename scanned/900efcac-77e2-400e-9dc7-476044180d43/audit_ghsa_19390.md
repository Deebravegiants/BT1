# [H] React Router allows a DoS via cache poisoning by forcing SPA mode

## Summary
Severity: High
Advisory: GHSA-f46r-rw29-r322
CVE: CVE-2025-43864
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-24
Source: https://github.com/advisories/GHSA-f46r-rw29-r322
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.2.0 <7.5.2

## Details
## Summary
After some research, it turns out that it is possible to force an application to switch to SPA mode by adding a header to the request. If the application uses SSR and is forced to switch to SPA, this causes an error that completely corrupts the page. If a cache system is in place, this allows the response containing the error to be cached, resulting in a cache poisoning that strongly impacts the availability of the application.

## Details
The vulnerable header is `X-React-Router-SPA-Mode`; adding it to a request sent to a page/endpoint using a loader throws an error. Here is [the vulnerable code](https://github.com/remix-run/react-router/blob/e6c53a0130559b4a9bd47f9cf76ea5b08a69868a/packages/react-router/lib/server-runtime/server.ts#L407) :

<img width="672" alt="Capture d’écran 2025-04-07 à 08 28 20" src="https://github.com/user-attachments/assets/0a0e9c41-70fd-4dba-9061-892dd6797291" />

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

![image](https://github.com/user-attachments/assets/d7d04e86-c549-4f4a-9200-2d1b6ac96aad)

3. Send a request to the endpoint using the loader (`/ssr` in our case) adding the following header:
```
X-React-Router-SPA-Mode: yes
```

Notice the difference between a request with and without the header;

**Normal request**
![Capture d’écran 2025-04-07 à 08 36 27](https://github.com/user-attachments/assets/da372b70-7c68-41c1-aac1-e5be94f22526)

**With the header**
![Capture d’écran 2025-04-07 à 08 37 01](https://github.com/user-attachments/assets/98101720-cb5b-44e9-bff5-463c0b4dab2a)
![image](https://github.com/user-attachments/assets/c16a101e-688c-4757-9e05-61308ed8a2de)

## Impact
If a system cache is in place, it is possible to poison the response by completely altering its content (*by an error message*), strongly impacting its availability, making the latter impractical via a cache-poisoning attack.

## Credits
- Rachid Allam (zhero;)
- Yasser Allam (inzo_)

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-f46r-rw29-r322
- https://nvd.nist.gov/vuln/detail/CVE-2025-43864
- https://github.com/remix-run/react-router/commit/c84302972a152d851cf5dd859ff332b354b70111
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/e6c53a0130559b4a9bd47f9cf76ea5b08a69868a/packages/react-router/lib/server-runtime/server.ts#L407
