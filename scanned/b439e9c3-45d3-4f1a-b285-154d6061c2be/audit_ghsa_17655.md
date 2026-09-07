# [M] urllib3 redirects are not disabled when retries are disabled on PoolManager instantiation

## Summary
Severity: Medium
Advisory: GHSA-pq67-6m6q-mj2v
CVE: CVE-2025-50181
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-18
Source: https://github.com/advisories/GHSA-pq67-6m6q-mj2v
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <2.5.0

## Details
urllib3 handles redirects and retries using the same mechanism, which is controlled by the `Retry` object. The most common way to disable redirects is at the request level, as follows:

```python
resp = urllib3.request("GET", "https://httpbin.org/redirect/1", redirect=False)
print(resp.status)
# 302
```

However, it is also possible to disable redirects, for all requests, by instantiating a `PoolManager` and specifying `retries` in a way that disable redirects:

```python
import urllib3

http = urllib3.PoolManager(retries=0)  # should raise MaxRetryError on redirect
http = urllib3.PoolManager(retries=urllib3.Retry(redirect=0))  # equivalent to the above
http = urllib3.PoolManager(retries=False)  # should return the first response

resp = http.request("GET", "https://httpbin.org/redirect/1")
```

However, the `retries` parameter is currently ignored, which means all the above examples don't disable redirects.

## Affected usages

Passing `retries` on `PoolManager` instantiation to disable redirects or restrict their number.

By default, requests and botocore users are not affected.

## Impact

Redirects are often used to exploit SSRF vulnerabilities. An application attempting to mitigate SSRF or open redirect vulnerabilities by disabling redirects at the PoolManager level will remain vulnerable.

## Remediation

You can remediate this vulnerability with the following steps:

 * Upgrade to a patched version of urllib3. If your organization would benefit from the continued support of urllib3 1.x, please contact [sethmichaellarson@gmail.com](mailto:sethmichaellarson@gmail.com) to discuss sponsorship or contribution opportunities.
 * Disable redirects at the `request()` level instead of the `PoolManager()` level.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-pq67-6m6q-mj2v
- https://nvd.nist.gov/vuln/detail/CVE-2025-50181
- https://github.com/urllib3/urllib3/commit/f05b1329126d5be6de501f9d1e3e36738bc08857
- https://github.com/urllib3/urllib3
- https://github.com/urllib3/urllib3/releases/tag/2.5.0
