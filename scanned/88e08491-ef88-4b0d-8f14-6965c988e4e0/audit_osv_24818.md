# [H] CVE-2023-27161

## Summary
Severity: High
Advisory: CVE-2023-27161
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-10
Source: https://osv.dev/vulnerability/CVE-2023-27161
Type: osv

## Details
Jellyfin up to v10.7.7 was discovered to contain a Server-Side Request Forgery (SSRF) via the component /Repositories. This vulnerability allows attackers to access network resources and sensitive information via a crafted POST request.

## References
- https://gist.github.com/b33t1e/5c067e0538a0b712dc3d59bd4b9a5952
- https://notes.sjtu.edu.cn/s/yJ9lPk09a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27161.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27161
- https://github.com/jellyfin/jellyfin
