# [C] CVE-2019-9750

## Summary
Severity: Critical
Advisory: CVE-2019-9750
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-9750
Type: osv

## Details
In IoTivity through 1.3.1, the CoAP server interface can be used for Distributed Denial of Service attacks using source IP address spoofing and UDP-based traffic amplification. The reflected traffic is 6 times bigger than spoofed requests. This occurs because the construction of a "4.01 Unauthorized" response is mishandled. NOTE: the vendor states "While this is an interesting attack, there is no plan for maintainer to fix, as we are migrating to IoTivity Lite."

## References
- https://jira.iotivity.org/browse/IOT-3267
