# [M] yuan1994 tpAdmin vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-qr7h-8pv2-xvx2
CVE: CVE-2023-1971
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-10
Source: https://github.com/advisories/GHSA-qr7h-8pv2-xvx2
Type: github-advisory

## Affected
- Packagist: `yuan1994/tpadmin` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** A vulnerability, which was classified as critical, was found in yuan1994 tpAdmin 1.3.12. Affected is the function remote of the file application\admin\controller\Upload.php. The manipulation of the argument url leads to server-side request forgery. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-225408. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1971
- https://github.com/yuan1994/tpAdmin
- https://tib36.github.io/2023/04/09/tpAdmin-SSRF
- https://vuldb.com/?ctiid.225408
- https://vuldb.com/?id.225408
