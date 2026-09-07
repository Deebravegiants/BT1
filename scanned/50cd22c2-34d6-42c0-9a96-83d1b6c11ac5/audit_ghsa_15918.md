# [M] Inventree Server-Side Request Forgery vulnerability exposes server port/internal IP

## Summary
Severity: Medium
Advisory: GHSA-vx3h-qwqw-r2wq
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-vx3h-qwqw-r2wq
Type: github-advisory

## Affected
- PyPI: `inventree` — affected >=0 <0.16.5

## Details
### Impact

The "download image from remote URL" feature can be abused by a malicious actor to potentially extract information about server side resources. Submitting a crafted URL (in place of a valid image) can raise a server side error, which is reported back to the user. 

This error message may contain sensitive information about the server side request, including information about the availability of the remote resource.

### Patches

The solution to this vulnerability is to prevent the server from returning any specific information about the observed exception. Instead, a generic error message is returned to the client.

This patch has been applied to the upcoming 0.17.0 release, and also back-ported to the 0.16.5 stable release.

### Workarounds

To avoid this issue with unpatched versions, the "download image from remote URL" feature can be disabled in InvenTree, preventing users from accessing this information. 

### References

Thanks to @febin0x10 for identifying this vulnerability and reporting it to us as per our security policy.

## References
- https://github.com/inventree/InvenTree/security/advisories/GHSA-vx3h-qwqw-r2wq
- https://github.com/inventree/InvenTree/commit/5759b60a48e7e178fb417a900ed543f29dc5dc86
- https://github.com/inventree/InvenTree
