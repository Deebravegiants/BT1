# [M] CVE-2022-3586

## Summary
Severity: Medium
Advisory: CVE-2022-3586
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-3586
Type: osv

## Details
A flaw was found in the Linux kernel’s networking code. A use-after-free was found in the way the sch_sfb enqueue function used the socket buffer (SKB) cb field after the same SKB had been enqueued (and freed) into a child qdisc. This flaw allows a local, unprivileged user to crash the system, causing a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3586.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3586
- https://www.zerodayinitiative.com/advisories/upcoming/
- https://github.com/torvalds/linux/commit/9efd23297cca
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
