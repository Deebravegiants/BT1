# [H] CVE-2022-1012

## Summary
Severity: High
Advisory: CVE-2022-1012
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-08-05
Source: https://osv.dev/vulnerability/CVE-2022-1012
Type: osv

## Details
A memory leak problem was found in the TCP source port generation algorithm in net/ipv4/tcp.c due to the small table perturb size. This flaw may allow an attacker to information leak and may cause a denial of service problem.

## References
- https://lore.kernel.org/lkml/20220427065233.2075-1-w%401wt.eu/T/
- https://security.netapp.com/advisory/ntap-20221020-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2064604
