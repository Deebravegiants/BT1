# [M] appneta tcpreplay get.c get_layer4_v6 heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2024-3024
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-28
Source: https://osv.dev/vulnerability/CVE-2024-3024
Type: osv

## Details
A vulnerability was found in appneta tcpreplay up to 4.4.4. It has been classified as problematic. This affects the function get_layer4_v6 of the file /tcpreplay/src/common/get.c. The manipulation leads to heap-based buffer overflow. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used. The identifier VDB-258333 was assigned to this vulnerability. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://docs.google.com/document/d/1wCIrViAJwGsO5afPBLLjRhO5RClsoUo3J9q1psLs84s/edit?usp=sharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3024.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3024
- https://vuldb.com/?submit.297866
- https://vuldb.com/?ctiid.258333
- https://drive.google.com/file/d/1zV9MSkfYLIrdtK3yczy1qbsJr_yN2fwH/view
- https://vuldb.com/?id.258333
