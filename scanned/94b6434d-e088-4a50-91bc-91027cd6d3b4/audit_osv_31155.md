# [M] firmware: qcom: scm: Fix missing read barrier in qcom_scm_get_tzmem_pool()

## Summary
Severity: Medium
Advisory: CVE-2024-58084
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58084
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: qcom: scm: Fix missing read barrier in qcom_scm_get_tzmem_pool()

Commit 2e4955167ec5 ("firmware: qcom: scm: Fix __scm and waitq
completion variable initialization") introduced a write barrier in probe
function to store global '__scm' variable.  We all known barriers are
paired (see memory-barriers.txt: "Note that write barriers should
normally be paired with read or address-dependency barriers"), therefore
accessing it from concurrent contexts requires read barrier.  Previous
commit added such barrier in qcom_scm_is_available(), so let's use that
directly.

Lack of this read barrier can result in fetching stale '__scm' variable
value, NULL, and dereferencing it.

Note that barrier in qcom_scm_is_available() satisfies here the control
dependency.

## References
- https://git.kernel.org/stable/c/b628510397b5cafa1f5d3e848a28affd1c635302
- https://git.kernel.org/stable/c/e03db7c1255ebabba5e1a447754faeb138de15a2
- https://git.kernel.org/stable/c/fee921e3c641f64185abee83f9a6e65f0b380682
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58084.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
