# [H] Astro's server source code is exposed to the public if sourcemaps are enabled

## Summary
Severity: High
Advisory: GHSA-49w6-73cw-chjr
CVE: CVE-2024-56159
CWE: CWE-219
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2024-12-19
Source: https://github.com/advisories/GHSA-49w6-73cw-chjr
Type: github-advisory

## Affected
- npm: `astro` — affected >=5.0.0-alpha.0 <5.0.8
- npm: `astro` — affected >=0 <4.16.18

## Details
### Summary
A bug in the build process allows any unauthenticated user to read parts of the server source code.

### Details
During build, along with client assets such as css and font files, the sourcemap files **for the server code** are moved to a publicly-accessible folder.
https://github.com/withastro/astro/blob/176fe9f113fd912f9b61e848b00bbcfecd6d5c2c/packages/astro/src/core/build/static-build.ts#L139

Any outside party can read them with an unauthorized HTTP GET request to the same server hosting the rest of the website.

While some server files are hashed, making their access obscure, the files corresponding to the file system router (those in `src/pages`) are predictably named. For example. the sourcemap file for `src/pages/index.astro` gets named `dist/client/pages/index.astro.mjs.map`.

### PoC
Here is one example of an affected open-source website:
https://creatorsgarten.org/pages/index.astro.mjs.map

<image width="500" height="263" src="https://github.com/user-attachments/assets/773c5532-87af-42b8-838e-8f5472bf9f68"/>

The file can be saved and opened using https://evanw.github.io/source-map-visualization/ to reconstruct the source code.

<image width="500" height="271" src="https://github.com/user-attachments/assets/7d35d0ca-3a29-4666-be21-cfefe311ac9d"/>

The above accurately mirrors the source code as seen in the repository: https://github.com/creatorsgarten/creatorsgarten.org/blob/main/src/pages/index.astro

<image width="500" height="298" src="https://github.com/user-attachments/assets/39e77197-8382-4556-a024-c526dacccc1c"/>


The above was found as the 4th result (and the first one on Astro 5.0+) when making the following search query on GitHub.com ([search results link](https://github.com/search?q=path%3Aastro.config.mjs+%40sentry%2Fastro&type=code)):
```
path:astro.config.mjs @sentry/astro
```

This vulnerability is the root cause of https://github.com/withastro/astro/issues/12703, which links to a simple stackblitz project demonstrating the vulnerability. Upon build, notice the contents of the `dist/client` (referred to as `config.build.client` in astro code) folder. All astro servers make the folder in question accessible to the public internet without any authentication. It contains `.map` files corresponding to the code that runs on the server.

### Impact
All **server-output** (SSR) projects on Astro 5 versions **v5.0.3** through **v5.0.6** (inclusive), that have **sourcemaps enabled**, either directly or through an add-on such as [sentry](https://github.com/getsentry/sentry-javascript/blob/develop/packages/astro/src/integration/index.ts#L50), are affected. The fix for **server-output** projects was released in **astro@5.0.7**.

Additionally, all **static-output** (SSG) projects built using Astro 4 versions **4.16.17 or older**, or Astro 5 versions **5.0.7 or older**, that have **sourcemaps enabled** are also affected. The fix for **static-output** projects was released in **astro@5.0.8**, and backported to Astro v4 in **astro@4.16.18**.

The immediate impact is limited to source code. Any secrets or environment variables are not exposed unless they are present verbatim in the source code.

There is no immediate loss of integrity within the the vulnerable server. However, it is possible to subsequently discover another vulnerability via the revealed source code .

There is no immediate impact to availability of the vulnerable server. However, the presence of an unsafe regular expression, for example, can quickly be exploited to subsequently compromise the availability.

- Network attack vector.
- Low attack complexity.
- No privileges required.
- No interaction required from an authorized user.
- Scope is limited to first party. Although the source code of closed-source third-party software may also be exposed. 

### Remediation
The fix for **server-output** projects was released in **astro@5.0.7**, and the fix for **static-output** projects was released in **astro@5.0.8** and backported to Astro v4 in **astro@4.16.18**. Users are advised to update immediately if they are using sourcemaps or an integration that enables sourcemaps.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-49w6-73cw-chjr
- https://nvd.nist.gov/vuln/detail/CVE-2024-56159
- https://github.com/withastro/astro/issues/12703
- https://github.com/withastro/astro/commit/039d022b1bbaacf9ea83071d27affc5318e0e515
- https://github.com/withastro/astro/commit/c879f501ff01b1a3c577de776a1f7100d78f8dd5
- https://github.com/getsentry/sentry-javascript/blob/develop/packages/astro/src/integration/index.ts#L50
- https://github.com/withastro/astro
- https://github.com/withastro/astro/blob/176fe9f113fd912f9b61e848b00bbcfecd6d5c2c/packages/astro/src/core/build/static-build.ts#L139
