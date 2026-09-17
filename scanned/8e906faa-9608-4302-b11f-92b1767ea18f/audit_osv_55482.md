# [C] CVE-2025-54490

## Summary
Severity: Critical
Advisory: CVE-2025-54490
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-54490
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the MFER parsing functionality of The Biosig Project libbiosig 3.9.0 and Master Branch (35a819fa). A specially crafted MFER file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.This vulnerability manifests on line 9090 of biosig.c on the current master branch (35a819fa), when the Tag is 64:

                else if (tag==64)     //0x40
                {
                    // preamble
                    char tmp[256];  // [1]
                    curPos += ifread(tmp,1,len,hdr);

In this case, the overflowed buffer is the newly-declared `tmp` \[1\] instead of `buf`. While `tmp` is larger than `buf`, having a size of 256 bytes, a stack overflow can still occur in cases where `len` is encoded using multiple octets and is greater than 256.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2234
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2234
