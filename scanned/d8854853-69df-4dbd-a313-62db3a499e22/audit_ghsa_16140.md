# [M] changedetection.io Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-cwgg-57xj-g77r
CVE: CVE-2024-51483
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-01
Source: https://github.com/advisories/GHSA-cwgg-57xj-g77r
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.47.5

## Details
### Summary
When a WebDriver is used to fetch files source:file:///etc/passwd can be used to retrieve local system files, where the more traditional file:///etc/passwd gets blocked

### Details
The root cause is the payload source:file:///etc/passwdpasses the regex [here](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L19) and also passes the check [here](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/processors/__init__.py#L35) where a traditional file:///etc/passwd would get blocked

### PoC
[CL-ChangeDetection.io Path Travsersal-311024-181039.pdf](https://github.com/user-attachments/files/17591630/CL-ChangeDetection.io.Path.Travsersal-311024-181039.pdf)



### Impact
It depends on where the webdriver is deployed but generally this is a high impact vulnerability

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-cwgg-57xj-g77r
- https://nvd.nist.gov/vuln/detail/CVE-2024-51483
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L19
- https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/processors/__init__.py#L35
- https://github.com/user-attachments/files/17591630/CL-ChangeDetection.io.Path.Travsersal-311024-181039.pdf
