# [M] CVE-2020-14059

## Summary
Severity: Medium
Advisory: CVE-2020-14059
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-14059
Type: osv

## Details
An issue was discovered in Squid 5.x before 5.0.3. Due to an Incorrect Synchronization, a Denial of Service can occur when processing objects in an SMP cache because of an Ipc::Mem::PageStack::pop ABA problem during access to the memory page/slot management list.

## References
- http://www.squid-cache.org/Advisories/SQUID-2020_5.txt
- https://security.netapp.com/advisory/ntap-20210312-0001/
- http://www.squid-cache.org/Versions/v5/changesets/squid-5-7a5af8db8e0377c06ed9ffbdcb1334389c7cd8ab.patch
