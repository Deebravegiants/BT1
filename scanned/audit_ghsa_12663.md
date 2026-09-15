# [H] Vite Server Options (server.fs.deny) can be bypassed using double forward-slash (//)

## Summary
Severity: High
Advisory: GHSA-353f-5xf4-qw67
CVE: CVE-2023-34092
CWE: CWE-200, CWE-50, CWE-706
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-353f-5xf4-qw67
Type: github-advisory

## Affected
- npm: `vite` — affected >=0 <2.9.16
- npm: `vite` — affected >=3.0.2 <3.2.7
- npm: `vite` — affected >=4.0.0 <4.0.5
- npm: `vite` — affected >=4.1.0 <4.1.5
- npm: `vite` — affected >=4.2.0 <4.2.3
- npm: `vite` — affected >=4.3.0 <4.3.9

## Details
The issue involves a security vulnerability in Vite where the server options can be bypassed using a double forward slash (`//`). This vulnerability poses a potential security risk as it can allow unauthorized access to sensitive directories and files.

### Steps to Fix. **Update Vite**: Ensure that you are using the latest version of Vite. Security issues like this are often fixed in newer releases.\n2. **Secure the server configuration**: In your `vite.config.js` file, review and update the server configuration options to restrict access to unauthorized requests or directories.

### Impact
Only users explicitly exposing the Vite dev server to the network (using `--host` or the [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host)) are affected and only files in the immediate Vite project root folder could be exposed.\n\n### Patches\nFixed in vite@**4.3.9**, vite@**4.2.3**, vite@**4.1.5**, vite@**4.0.5** and in the latest minors of the previous two majors, vite@**3.2.7** and vite@**2.9.16**.

 ### Details 
Vite serves the application with under the root-path of the project while running on the dev mode. By default, Vite uses the server option fs.deny to protect sensitive files. But using a simple double forward-slash, we can bypass this restriction. \n\n### PoC\n1. Create a new latest project of Vite using any package manager. (here I'm using react and vue templates and pnpm for testing)\n2. Serve the application on dev mode using `pnpm run dev`.\n3. Directly access the file via url using double forward-slash (`//`) (e.g: `//.env`, `//.env.local`)\n4. The server option `fs.deny` was successfully bypassed.

Proof Images: ![proof-1](https://user-images.githubusercontent.com/30733517/241105344-6ecbc7f6-57b7-45c7-856a-6421a577dda1.png)\n![proof-2](https://user-images.githubusercontent.com/30733517/241105349-ab9561e7-8aff-4f29-97f9-b784e673c122.png)

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-353f-5xf4-qw67
- https://nvd.nist.gov/vuln/detail/CVE-2023-34092
- https://github.com/vitejs/vite/pull/13348
- https://github.com/vitejs/vite/commit/813ddd6155c3d54801e264ba832d8347f6f66b32
- https://github.com/vitejs/vite
- https://security.snyk.io/package/npm/vite/3.2.0-beta.4
