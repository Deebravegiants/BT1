# [C] CVE-2020-12658

## Summary
Severity: Critical
Advisory: CVE-2020-12658
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-31
Source: https://osv.dev/vulnerability/CVE-2020-12658
Type: osv

## Details
gssproxy (aka gss-proxy) before 0.8.3 does not unlock cond_mutex before pthread exit in gp_worker_main() in gp_workers.c. NOTE: An upstream comment states "We are already on a shutdown path when running the code in question, so a DoS there doesn't make any sense, and there has been no additional information provided us (as upstream) to indicate why this would be a problem.

## References
- https://github.com/gssapi/gssproxy/compare/v0.8.2...v0.8.3
- https://lists.debian.org/debian-lts-announce/2021/01/msg00004.html
- https://pagure.io/gssproxy/c/cb761412e299ef907f22cd7c4146d50c8a792003?branch=master
- https://github.com/gssapi/gssproxy/commit/cb761412e299ef907f22cd7c4146d50c8a792003
