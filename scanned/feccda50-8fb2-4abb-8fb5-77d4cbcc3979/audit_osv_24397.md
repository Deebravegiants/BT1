# [H] novel-plus list MenuService sql injection

## Summary
Severity: High
Advisory: CVE-2023-1594
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-03-23
Source: https://osv.dev/vulnerability/CVE-2023-1594
Type: osv

## Details
A vulnerability, which was classified as critical, was found in novel-plus 3.6.2. Affected is the function MenuService of the file sys/menu/list. The manipulation of the argument sort leads to sql injection. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. VDB-223662 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1594.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1594
- https://vuldb.com/?id.223662
- https://vuldb.com/?ctiid.223662
- https://github.com/OYyunshen/Poc/blob/main/Novel-PlusV3.6.2Sqli.pdf
