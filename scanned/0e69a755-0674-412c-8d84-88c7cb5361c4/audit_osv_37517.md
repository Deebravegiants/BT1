# [H] perf/x86: Fix potential bad container_of in intel_pmu_hw_config

## Summary
Severity: High
Advisory: CVE-2026-31782
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31782
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/x86: Fix potential bad container_of in intel_pmu_hw_config

Auto counter reload may have a group of events with software events
present within it. The software event PMU isn't the x86_hybrid_pmu and
a container_of operation in intel_pmu_set_acr_caused_constr (via the
hybrid helper) could cause out of bound memory reads. Avoid this by
guarding the call to intel_pmu_set_acr_caused_constr with an
is_x86_event check.

## References
- https://git.kernel.org/stable/c/bfee04838f636d064bc92075c65c95f739003804
- https://git.kernel.org/stable/c/dbde07f06226438cd2cf1179745fa1bec5d8914a
- https://git.kernel.org/stable/c/e435a30ca6fe14c9611b1fc731c98a6d28410247
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31782.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31782
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
