# [M] CVE-2019-14891

## Summary
Severity: Medium
Advisory: CVE-2019-14891
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-14891
Type: osv

## Details
A flaw was found in cri-o, as a result of all pod-related processes being placed in the same memory cgroup. This can result in container management (conmon) processes being killed if a workload process triggers an out-of-memory (OOM) condition for the cgroup. An attacker could abuse this flaw to get host network access on an cri-o host.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14891
