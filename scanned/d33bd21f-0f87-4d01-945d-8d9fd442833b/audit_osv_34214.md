# [M] CVE-2025-55904

## Summary
Severity: Medium
Advisory: CVE-2025-55904
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-55904
Type: osv

## Details
Open5GS v2.7.5, prior to commit 67ba7f92bbd7a378954895d96d9d7b05d5b64615, is vulnerable to a NULL pointer dereference when a multipart/related HTTP POST request with an empty HTTP body is sent to the SBI of either AMF, AUSF, BSF, NRF, NSSF, PCF, SMF, UDM, or UDR, resulting in a denial of service. This occurs in the parse_multipart function in lib/sbi/message.c.

## References
- https://github.com/tsiamoulis/vuln-research/tree/main/CVE-2025-55904
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55904.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55904
- https://github.com/open5gs/open5gs/issues/3942
- https://github.com/open5gs/open5gs/commit/67ba7f92bbd7a378954895d96d9d7b05d5b64615
