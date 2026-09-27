# [M] CVE-2025-64011

## Summary
Severity: Medium
Advisory: CVE-2025-64011
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-12
Source: https://osv.dev/vulnerability/CVE-2025-64011
Type: osv

## Details
Nextcloud Server 30.0.0 is vulnerable to an Insecure Direct Object Reference (IDOR) in the /core/preview endpoint. Any authenticated user can access previews of arbitrary files belonging to other users by manipulating the fileId parameter. This allows unauthorized disclosure of sensitive data, such as text files or images, without prior sharing permissions.

## References
- https://drive.google.com/file/d/1eD3PN-u1caZYgGH96XHmJ7h_OBXEAHW4/view?usp=sharing
- https://gist.github.com/tarekramm/586dfe2d113fedfee6d71182570fc090
- https://nextcloud.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64011.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64011
