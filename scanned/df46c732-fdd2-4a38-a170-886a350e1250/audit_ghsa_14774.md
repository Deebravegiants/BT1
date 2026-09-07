# [M] urllib3's Proxy-Authorization request header isn't stripped during cross-origin redirects

## Summary
Severity: Medium
Advisory: GHSA-34jh-p97f-mpxf
CVE: CVE-2024-37891
CWE: CWE-669
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-34jh-p97f-mpxf
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <1.26.19
- PyPI: `urllib3` — affected >=2.0.0 <2.2.2

## Details
When using urllib3's proxy support with `ProxyManager`, the `Proxy-Authorization` header is only sent to the configured proxy, as expected.

However, when sending HTTP requests *without* using urllib3's proxy support, it's possible to accidentally configure the `Proxy-Authorization` header even though it won't have any effect as the request is not using a forwarding proxy or a tunneling proxy. In those cases, urllib3 doesn't treat the `Proxy-Authorization` HTTP header as one carrying authentication material and thus doesn't strip the header on cross-origin redirects.

Because this is a highly unlikely scenario, we believe the severity of this vulnerability is low for almost all users. Out of an abundance of caution urllib3 will automatically strip the `Proxy-Authorization` header during cross-origin redirects to avoid the small chance that users are doing this on accident.

Users should use urllib3's proxy support or disable automatic redirects to achieve safe processing of the `Proxy-Authorization` header, but we still decided to strip the header by default in order to further protect users who aren't using the correct approach.

## Affected usages

We believe the number of usages affected by this advisory is low. It requires all of the following to be true to be exploited:

* Setting the `Proxy-Authorization` header without using urllib3's built-in proxy support.
* Not disabling HTTP redirects.
* Either not using an HTTPS origin server or for the proxy or target origin to redirect to a malicious origin.

## Remediation

* Using the `Proxy-Authorization` header with urllib3's `ProxyManager`.
* Disabling HTTP redirects using `redirects=False` when sending requests.
* Not using the `Proxy-Authorization` header.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-34jh-p97f-mpxf
- https://nvd.nist.gov/vuln/detail/CVE-2024-37891
- https://github.com/urllib3/urllib3/commit/40b6d1605814dd1db0a46e202d6e56f2e4c9a468
- https://github.com/urllib3/urllib3/commit/accff72ecc2f6cf5a76d9570198a93ac7c90270e
- https://github.com/urllib3/urllib3
- https://lists.debian.org/debian-lts-announce/2024/12/msg00020.html
- https://security.netapp.com/advisory/ntap-20240822-0003
- https://www.vicarius.io/vsociety/posts/proxy-authorization-header-handling-vulnerability-in-urllib3-cve-2024-37891
