# [H] CVE-2022-48217

## Summary
Severity: High
Advisory: CVE-2022-48217
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-04
Source: https://osv.dev/vulnerability/CVE-2022-48217
Type: osv

## Details
The tf_remapper_node component 1.1.1 for Robot Operating System (ROS) allows attackers, who control the source code of a different node in the same ROS application, to change a robot's behavior. This occurs because a topic name depends on the attacker-controlled old_tf_topic_name and/or new_tf_topic_name parameter. NOTE: the vendor's position is "it is the responsibility of the programmer to make sure that only known and required parameters are set and unexpected parameters are not."

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48217.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48217
- https://github.com/tradr-project/tf_remapper_cpp/issues/1
