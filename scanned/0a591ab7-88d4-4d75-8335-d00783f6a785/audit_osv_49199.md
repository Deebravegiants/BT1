# [H] CVE-2018-5391

## Summary
Severity: High
Advisory: CVE-2018-5391
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-5391
Type: osv

## Details
The Linux kernel, versions 3.9+, is vulnerable to a denial of service attack with low rates of specially modified packets targeting IP fragment re-assembly. An attacker may cause a denial of service condition by sending specially crafted IP fragments. Various vulnerabilities in IP fragmentation have been discovered and fixed over the years. The current vulnerability (CVE-2018-5391) became exploitable in the Linux kernel with the increase of the IP fragment reassembly queue size.

## References
- https://support.f5.com/csp/article/K74374841?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/3740-1/
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2018-004.txt
- https://access.redhat.com/errata/RHSA-2018:2791
- https://access.redhat.com/errata/RHSA-2018:2846
- https://access.redhat.com/errata/RHSA-2018:2924
- https://access.redhat.com/errata/RHSA-2018:3540
- https://access.redhat.com/errata/RHSA-2018:3590
- https://cert-portal.siemens.com/productcert/pdf/ssa-377115.pdf
- https://usn.ubuntu.com/3742-2/
- http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20200115-01-linux-en
- https://usn.ubuntu.com/3740-2/
- https://www.kb.cert.org/vuls/id/641765
- https://access.redhat.com/errata/RHSA-2018:2925
- https://access.redhat.com/errata/RHSA-2018:3586
- https://usn.ubuntu.com/3741-2/
- http://www.openwall.com/lists/oss-security/2019/07/06/3
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3096
- http://www.securityfocus.com/bid/105108
