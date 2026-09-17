# [M] obgm libcoap Configuration File coap_oscore.c get_split_entry stack-based overflow

## Summary
Severity: Medium
Advisory: CVE-2024-0962
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-01-27
Source: https://osv.dev/vulnerability/CVE-2024-0962
Type: osv

## Details
A vulnerability was found in obgm libcoap 4.3.4. It has been rated as critical. Affected by this issue is the function get_split_entry of the file src/coap_oscore.c of the component Configuration File Handler. The manipulation leads to stack-based buffer overflow. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue. VDB-252206 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0962.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0962
- https://vuldb.com/?id.252206
- https://github.com/obgm/libcoap/issues/1310
- https://github.com/obgm/libcoap/issues/1310#issue-2099860835
- https://vuldb.com/?ctiid.252206
- https://github.com/obgm/libcoap/pull/1311
