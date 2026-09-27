# [M] CVE-2020-18976

## Summary
Severity: Medium
Advisory: CVE-2020-18976
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-25
Source: https://osv.dev/vulnerability/CVE-2020-18976
Type: osv

## Details
Buffer Overflow in Tcpreplay v4.3.2 allows attackers to cause a Denial of Service via the 'do_checksum' function in 'checksum.c'. It can be triggered by sending a crafted pcap file to the 'tcpreplay-edit' binary. This issue is different than CVE-2019-8381.

## References
- https://github.com/appneta/tcpreplay/issues/556
