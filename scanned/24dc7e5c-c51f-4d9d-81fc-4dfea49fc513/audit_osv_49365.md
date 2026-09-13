# [M] CVE-2019-1125

## Summary
Severity: Medium
Advisory: CVE-2019-1125
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-09-03
Source: https://osv.dev/vulnerability/CVE-2019-1125
Type: osv

## Details
An information disclosure vulnerability exists when certain central processing units (CPU) speculatively access memory. An attacker who successfully exploited the vulnerability could read privileged data across trust boundaries.
To exploit this vulnerability, an attacker would have to log on to an affected system and run a specially crafted application. The vulnerability would not allow an attacker to elevate user rights directly, but it could be used to obtain information that could be used to try to compromise the affected system further.
On January 3, 2018, Microsoft released an advisory and security updates related to a newly-discovered class of hardware vulnerabilities (known as Spectre) involving speculative execution side channels that affect AMD, ARM, and Intel CPUs to varying degrees. This vulnerability, released on August 6, 2019, is a variant of the Spectre Variant 1 speculative execution side channel vulnerability and has been assigned CVE-2019-1125.
Microsoft released a security update on July 9, 2019 that addresses the vulnerability through a software change that mitigates how the CPU speculatively accesses memory. Note that this vulnerability does not require a microcode update from your device OEM.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10297
- http://packetstormsecurity.com/files/156337/SWAPGS-Attack-Proof-Of-Concept.html
- https://access.redhat.com/errata/RHSA-2019:2600
- https://access.redhat.com/errata/RHSA-2019:3220
- https://access.redhat.com/errata/RHSA-2019:3011
- http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20200408-01-swapgs-en
- https://access.redhat.com/errata/RHBA-2019:3248
- https://access.redhat.com/errata/RHSA-2019:2730
- https://access.redhat.com/errata/RHSA-2019:2899
- https://access.redhat.com/errata/RHSA-2019:2900
- https://access.redhat.com/errata/RHBA-2019:2824
- https://www.synology.com/security/advisory/Synology_SA_19_32
- https://access.redhat.com/errata/RHSA-2019:2975
- https://access.redhat.com/errata/RHSA-2019:2609
- https://access.redhat.com/errata/RHSA-2019:2695
- https://access.redhat.com/errata/RHSA-2019:2696
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1125
