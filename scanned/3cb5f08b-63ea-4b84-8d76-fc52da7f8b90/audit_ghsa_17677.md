# [M] urllib3 does not control redirects in browsers and Node.js

## Summary
Severity: Medium
Advisory: GHSA-48p4-8xcf-vxj5
CVE: CVE-2025-50182
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-18
Source: https://github.com/advisories/GHSA-48p4-8xcf-vxj5
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=2.2.0 <2.5.0

## Details
urllib3 [supports](https://urllib3.readthedocs.io/en/2.4.0/reference/contrib/emscripten.html) being used in a Pyodide runtime utilizing the [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) or falling back on [XMLHttpRequest](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest). This means you can use Python libraries to make HTTP requests from your browser or Node.js. Additionally, urllib3 provides [a mechanism](https://urllib3.readthedocs.io/en/2.4.0/user-guide.html#retrying-requests) to control redirects.

However, the `retries` and `redirect` parameters are ignored with Pyodide; the runtime itself determines redirect behavior.


## Affected usages

Any code which relies on urllib3 to control the number of redirects for an HTTP request in a Pyodide runtime.


## Impact

Redirects are often used to exploit SSRF vulnerabilities. An application attempting to mitigate SSRF or open redirect vulnerabilities by disabling redirects may remain vulnerable if a Pyodide runtime redirect mechanism is unsuitable.


## Remediation

If you use urllib3 in Node.js, upgrade to a patched version of urllib3.

Unfortunately, browsers provide no suitable way which urllib3 can use: `XMLHttpRequest` provides no control over redirects, the Fetch API returns `opaqueredirect` responses lacking data when redirects are controlled manually. Expect default browser behavior for redirects.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-48p4-8xcf-vxj5
- https://nvd.nist.gov/vuln/detail/CVE-2025-50182
- https://github.com/urllib3/urllib3/commit/7eb4a2aafe49a279c29b6d1f0ed0f42e9736194f
- https://github.com/urllib3/urllib3
- https://github.com/urllib3/urllib3/releases/tag/2.5.0
