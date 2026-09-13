# [M] Open5GS AMF client.c denial of service

## Summary
Severity: Medium
Advisory: CVE-2022-3299
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-3299
Type: osv

## Details
A vulnerability was found in Open5GS up to 2.4.10. It has been declared as problematic. Affected by this vulnerability is an unknown functionality in the library lib/sbi/client.c of the component AMF. The manipulation leads to denial of service. The attack can be launched remotely. The name of the patch is 724fa568435dae45ef0c3a48b2aabde052afae88. It is recommended to apply a patch to fix this issue. The identifier VDB-209545 was assigned to this vulnerability.

## References
- https://vuldb.com/?id.209545
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3299.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3299
- https://github.com/open5gs/open5gs/issues/1769
- https://github.com/open5gs/open5gs/commit/724fa568435dae45ef0c3a48b2aabde052afae88
