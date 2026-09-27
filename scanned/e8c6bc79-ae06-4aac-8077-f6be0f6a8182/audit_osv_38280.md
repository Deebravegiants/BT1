# [M] CVE-2026-36908

## Summary
Severity: Medium
Advisory: CVE-2026-36908
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-36908
Type: osv

## Details
A stack overflow in the AP4_Array<AP4_TrunAtom::Entry>::EnsureCapacity component of axiomatic-systems Bento4 before v1.8.9allows attackers to cause a Denial of Service (DoS) via a crafted MP4 file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/36xxx/CVE-2026-36908.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-36908
- https://github.com/Aleksoid1978/MPC-BE/issues/1005
- https://github.com/axiomatic-systems/Bento4/issues/842
- https://github.com/z1r00/fuzz_vuln/blob/main/Bento4/mp42aac/poc4.zip
