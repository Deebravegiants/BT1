# [H] c-blosc2 ndlz4x4.c ndlz4_decompress heap-based overflow

## Summary
Severity: High
Advisory: CVE-2024-3204
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-3204
Type: osv

## Details
A vulnerability has been found in c-blosc2 up to 2.13.2 and classified as critical. Affected by this vulnerability is the function ndlz4_decompress of the file /src/c-blosc2/plugins/codecs/ndlz/ndlz4x4.c. The manipulation leads to heap-based buffer overflow. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 2.14.3 is able to address this issue. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-259051.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3204.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3204
- https://vuldb.com/?id.259051
- https://vuldb.com/?submit.304557
- https://vuldb.com/?ctiid.259051
- https://github.com/Blosc/c-blosc2/releases/tag/v2.14.3
- https://drive.google.com/drive/folders/1T1k3UeS09m65LjVXExUuZfedNQPWQWCo?usp=sharing
