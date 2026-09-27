# [H] drm/amd/display: Fix slab-use-after-free on hdcp_work

## Summary
Severity: High
Advisory: CVE-2025-21968
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21968
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix slab-use-after-free on hdcp_work

[Why]
A slab-use-after-free is reported when HDCP is destroyed but the
property_validate_dwork queue is still running.

[How]
Cancel the delayed work when destroying workqueue.

(cherry picked from commit 725a04ba5a95e89c89633d4322430cfbca7ce128)

## References
- https://git.kernel.org/stable/c/06acfdef370ae018dad9592369e2d2fd9a40c09e
- https://git.kernel.org/stable/c/1397715b011bcdc6ad91b17df7acaee301e89db5
- https://git.kernel.org/stable/c/378b361e2e30e9729f9a7676f7926868d14f4326
- https://git.kernel.org/stable/c/4964dbc4191ab436877a5e3ecd9c67a4e50b7c36
- https://git.kernel.org/stable/c/93d701064e56788663d7c5918fbe5e060d5df587
- https://git.kernel.org/stable/c/bac7b8b1a3f1a86eeec85835af106cbdc2b9d9f7
- https://git.kernel.org/stable/c/e65e7bea220c3ce8c4c793b4ba35557f4994ab2b
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21968.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
