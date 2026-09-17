# [M] CVE-2021-36979

## Summary
Severity: Medium
Advisory: CVE-2021-36979
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-36979
Type: osv

## Details
Unicorn Engine 1.0.2 has an out-of-bounds write in tb_flush_armeb (called from cpu_arm_exec_armeb and tcg_cpu_exec_armeb).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZ6LOCJXHQVU6SCJLFDJINBOVJYYENLX/
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/unicorn/OSV-2020-2305.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=30391
- https://github.com/unicorn-engine/unicorn/commit/bf1713d9e011b55ca1f502a6779fc4722b4bb077
