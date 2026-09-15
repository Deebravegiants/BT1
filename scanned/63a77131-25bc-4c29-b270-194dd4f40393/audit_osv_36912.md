# [M] Improper Validation of Array Index in Packetbeat Leading to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-26932
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-26932
Type: osv

## Details
Improper Validation of Array Index (CWE-129) in the PostgreSQL protocol parser in Packetbeat can lead Denial of Service via Input Data Manipulation (CAPEC-153). An attacker can send a specially crafted packet causing a Go runtime panic that terminates the Packetbeat process. This vulnerability requires the pgsql protocol to be explicitly enabled and configured to monitor traffic on the targeted port.

## References
- https://discuss.elastic.co/t/packetbeat-8-19-11-9-2-5-security-update-esa-2026-10/385247
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26932.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26932
