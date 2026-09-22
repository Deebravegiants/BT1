# [H] Unconditionally adding an event to the epoll causes excessive CPU consumption

## Summary
Severity: High
Advisory: CVE-2023-5632
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-18
Source: https://osv.dev/vulnerability/CVE-2023-5632
Type: osv

## Details
In Eclipse Mosquito before and including 2.0.5, establishing a connection to the mosquitto server without sending data causes the EPOLLOUT event to be added, which results excessive CPU consumption. This could be used by a malicious actor to perform denial of service type attack. This issue is fixed in 2.0.6

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5632.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5632
- https://github.com/eclipse/mosquitto/commit/18bad1ff32435e523d7507e9b2ce0010124a8f2d
- https://github.com/eclipse/mosquitto/pull/2053
- https://github.com/eclipse/mosquitto
