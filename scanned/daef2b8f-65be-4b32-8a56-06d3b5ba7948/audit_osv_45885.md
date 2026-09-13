# [H] JLSEC-2026-441

## Summary
Severity: High
Advisory: JLSEC-2026-441
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-441
Type: osv

## Affected
- Julia: `libwebp_jll` — affected >=0 <1.3.2+0

## Details
Heap buffer overflow in libwebp in Google Chrome prior to 116.0.5845.187 and libwebp 1.3.2 allowed a remote attacker to perform an out of bounds memory write via a crafted HTML page. (Chromium security severity: Critical)

## References
- http://www.openwall.com/lists/oss-security/2023/09/21/4
- http://www.openwall.com/lists/oss-security/2023/09/22/1
- http://www.openwall.com/lists/oss-security/2023/09/22/3
- http://www.openwall.com/lists/oss-security/2023/09/22/4
- http://www.openwall.com/lists/oss-security/2023/09/22/5
- http://www.openwall.com/lists/oss-security/2023/09/22/6
- http://www.openwall.com/lists/oss-security/2023/09/22/7
- http://www.openwall.com/lists/oss-security/2023/09/22/8
- http://www.openwall.com/lists/oss-security/2023/09/26/1
- http://www.openwall.com/lists/oss-security/2023/09/26/7
- http://www.openwall.com/lists/oss-security/2023/09/28/1
- http://www.openwall.com/lists/oss-security/2023/09/28/2
- http://www.openwall.com/lists/oss-security/2023/09/28/4
- https://adamcaudill.com/2023/09/14/whose-cve-is-it-anyway/
- https://blog.isosceles.com/the-webp-0day/
- https://bugzilla.suse.com/show_bug.cgi?id=1215231
- https://chromereleases.googleblog.com/2023/09/stable-channel-update-for-desktop_11.html
- https://crbug.com/1479274
- https://en.bandisoft.com/honeyview/history/
- https://github.com/webmproject/libwebp/commit/902bc9190331343b2017211debcec8d2ab87e17a
