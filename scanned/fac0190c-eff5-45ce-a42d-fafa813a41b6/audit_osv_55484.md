# [C] CVE-2025-54492

## Summary
Severity: Critical
Advisory: CVE-2025-54492
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-54492
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the MFER parsing functionality of The Biosig Project libbiosig 3.9.0 and Master Branch (35a819fa). A specially crafted MFER file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.This vulnerability manifests on line 9141 of biosig.c on the current master branch (35a819fa), when the Tag is 67:

                else if (tag==67)     //0x43: Sample skew
                {
                    int skew=0;     // [1]
                    curPos += ifread(&skew, 1, len,hdr);

In this case, the address of the newly-defined integer `skew` \[1\] is overflowed instead of `buf`. This means a stack overflow can occur using much smaller values of `len` in this code path.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2234
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2234
