# [H] c-blosc2 ndlz8x8.c ndlz8_decompress heap-based overflow

## Summary
Severity: High
Advisory: CVE-2024-3203
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-3203
Type: osv

## Details
A vulnerability, which was classified as critical, was found in c-blosc2 up to 2.13.2. Affected is the function ndlz8_decompress of the file /src/c-blosc2/plugins/codecs/ndlz/ndlz8x8.c. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 2.14.3 is able to address this issue. It is recommended to upgrade the affected component. VDB-259050 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3203.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3203
- https://vuldb.com/?id.259050
- https://vuldb.com/?submit.304556
- https://vuldb.com/?ctiid.259050
- https://github.com/Blosc/c-blosc2/releases/tag/v2.14.3
- https://drive.google.com/drive/folders/1T1k3UeS09m65LjVXExUuZfedNQPWQWCo?usp=sharing
