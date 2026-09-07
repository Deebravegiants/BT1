# [H] @angular/common: Denial of Service (DoS) via OOM in Date Formatting (formatDate)

## Summary
Severity: High
Advisory: GHSA-48r7-hpm6-gfxm
CVE: CVE-2026-54268
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-48r7-hpm6-gfxm
Type: github-advisory

## Affected
- npm: `@angular/common` — affected >=22.0.0-next.0 <22.0.1
- npm: `@angular/common` — affected >=21.0.0-next.0 <21.2.17
- npm: `@angular/common` — affected >=20.0.0-next.0 <20.3.25
- npm: `@angular/common` — affected >=0

## Details
A Denial of Service (DoS) vulnerability exists in the `@angular/common` package of the Angular framework. The `formatDate` function, which is also utilized by the standard Angular `DatePipe`, does not properly limit or validate the length of the `format` parameter. 

When parsing a maliciously crafted, excessively long date format string (e.g., a repeating pattern or very large string), the internal parser splits the string iteratively using a regular expression loop. This results in uncontrolled resource consumption (high CPU utilization and excessive memory allocations), leading to a Denial of Service (DoS).


### Impact

#### 1. Server-Side Rendering (SSR)
In Angular applications that leverage Server-Side Rendering, an attacker can supply a malicious payload with an excessively long date format string. Processing this on the server causes high CPU usage and triggers a `JavaScript heap out of memory` crash, rendering the application unavailable to all users.

#### 2. Client-Side Rendering (CSR)
In standard client-side applications, executing the vulnerable function with an excessively long format string blocks the browser's main thread, causing the browser tab to freeze and become completely unresponsive.

### Patched Versions
* 22.0.1  
* 21.2.17  
* 20.3.25

### Attack Preconditions
For this vulnerability to be exploitable, both of the following conditions must be met:
1. **Vulnerable Component Usage:** The application must format dates using the `formatDate` utility or the `DatePipe`.
2. **Attacker-Controlled Parameter:** The date format string passed to these utilities must be customizable or directly controlled by untrusted user input (e.g., parsed from query parameters, user preferences, or API responses).

*If the date format is hardcoded (e.g., `'mediumDate'`, `'shortTime'`, or static strings) or properly validated to be within a reasonable length limit, the application is not vulnerable.*

## References
- https://github.com/angular/angular/security/advisories/GHSA-48r7-hpm6-gfxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54268
- https://github.com/angular/angular/pull/69197
- https://github.com/angular/angular/commit/eeb03f4ea310e2e51ba5d53a421ec7b418e186cd
- https://github.com/angular/angular
