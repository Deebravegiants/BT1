# [H] CVE-2022-2853

## Summary
Severity: High
Advisory: CVE-2022-2853
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-2853
Type: osv

## Details
Heap buffer overflow in Downloads in Google Chrome on Android prior to 104.0.5112.101 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4NMJURTG5RO3TGD7ZMIQ6Z4ZZ3SAVYE/
- https://issues.chromium.org/issues/40060491
- http://packetstormsecurity.com/files/169459/Chrome-offline_items_collection-OfflineContentAggregator-OnItemRemoved-Heap-Buffer-Overflow.html
- https://crbug.com/1350097
- https://chromereleases.googleblog.com/2022/08/stable-channel-update-for-desktop_16.html
