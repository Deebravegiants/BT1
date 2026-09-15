# [C] Plane allows server side request forgery via /_next/image endpoint

## Summary
Severity: Critical
Advisory: CVE-2024-47830
Aliases: GHSA-39gx-38xf-c348
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H)
Published: 2024-10-11
Source: https://osv.dev/vulnerability/CVE-2024-47830
Type: osv

## Details
Plane is an open-source project management tool. Plane uses the ** wildcard support to retrieve the image from any hostname as in /web/next.config.js. This may permit an attacker to induce the server side into performing requests to unintended locations. This vulnerability is fixed in 0.23.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47830.json
- https://github.com/makeplane/plane/security/advisories/GHSA-39gx-38xf-c348
- https://nvd.nist.gov/vuln/detail/CVE-2024-47830
- https://github.com/makeplane/plane/commit/b9f78ba42b70461c8c1d26638fa8b9beef6a96a1
