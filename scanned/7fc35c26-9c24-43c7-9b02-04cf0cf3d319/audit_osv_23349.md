# [C] CVE-2022-48198

## Summary
Severity: Critical
Advisory: CVE-2022-48198
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-01
Source: https://osv.dev/vulnerability/CVE-2022-48198
Type: osv

## Details
The ntpd_driver component before 1.3.0 and 2.x before 2.2.0 for Robot Operating System (ROS) allows attackers, who control the source code of a different node in the same ROS application, to change a robot's behavior. This occurs because a topic name depends on the attacker-controlled time_ref_topic parameter.

## References
- https://github.com/vooon/ntpd_driver/compare/1.2.0...1.3.0
- https://github.com/vooon/ntpd_driver/compare/2.1.0...2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48198.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48198
- https://github.com/vooon/ntpd_driver/issues/9
