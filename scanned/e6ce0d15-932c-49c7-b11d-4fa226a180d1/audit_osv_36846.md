# [C] Critical Heap Out-of-bounds Access in `pf_cluster_stats()` via Malicious /initialpose Covariance -- Potential Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-26011
Aliases: GHSA-mgj5-g2p6-gc5x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-26011
Type: osv

## Details
navigation2 is a ROS 2 Navigation Framework and System. In 1.3.11 and earlier, a critical heap out-of-bounds write vulnerability exists in Nav2 AMCL's particle filter clustering logic. By publishing a single crafted geometry_msgs/PoseWithCovarianceStamped message with extreme covariance values to the /initialpose topic, an unauthenticated attacker on the same ROS 2 DDS domain can trigger a negative index write (set->clusters[-1]) into heap memory preceding the allocated buffer. In Release builds, the sole boundary check (assert) is compiled out, leaving zero runtime protection. This primitive allows controlled corruption of the heap chunk metadata(at least the size of the heap chunk where the set->clusters is in is controllable by the attacker), potentially leading to further exploitation. At minimum, it provides a reliable single-packet denial of service that kills localization and halts all navigation.

## References
- https://github.com/ros-navigation/navigation2/releases/tag/1.3.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26011.json
- https://github.com/ros-navigation/navigation2/security/advisories/GHSA-mgj5-g2p6-gc5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-26011
- https://github.com/ros-navigation/navigation2/commit/d09ea82477ce9234678a6febf6890235e0a7ce12
