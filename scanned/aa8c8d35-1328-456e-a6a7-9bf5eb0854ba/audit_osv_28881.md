# [H] Collabora Online's remote host TLS certificates are not fully verified

## Summary
Severity: High
Advisory: CVE-2024-37311
Aliases: GHSA-hvhm-5c44-977x
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-08-23
Source: https://osv.dev/vulnerability/CVE-2024-37311
Type: osv

## Details
Collabora Online is a collaborative online office suite based on LibreOffice. In affected versions of Collabora Online, https connections from coolwsd to other hosts may incompletely verify the remote host's certificate's against the full chain of trust. This vulnerability is fixed in Collabora Online 24.04.4.3, 23.05.14.1, and 22.05.23.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37311.json
- https://github.com/CollaboraOnline/online/security/advisories/GHSA-hvhm-5c44-977x
- https://nvd.nist.gov/vuln/detail/CVE-2024-37311
