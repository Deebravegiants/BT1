# [M] CVE-2024-24155

## Summary
Severity: Medium
Advisory: CVE-2024-24155
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-24155
Type: osv

## Details
Bento4 v1.5.1-628 contains a Memory leak on AP4_Movie::AP4_Movie, parsing tracks and added into m_Tracks list, but mp42aac cannot correctly delete when we got an no audio track found error. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted mp4 file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24155.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24155
- https://github.com/axiomatic-systems/Bento4/issues/919
