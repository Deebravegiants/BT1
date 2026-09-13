# [M] CVE-2017-11613

## Summary
Severity: Medium
Advisory: CVE-2017-11613
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11613
Type: osv

## Details
In LibTIFF 4.0.8, there is a denial of service vulnerability in the TIFFOpen function. A crafted input will lead to a denial of service attack. During the TIFFOpen process, td_imagelength is not checked. The value of td_imagelength can be directly controlled by an input file. In the ChopUpSingleUncompressedStrip function, the _TIFFCheckMalloc function is called based on td_imagelength. If we set the value of td_imagelength close to the amount of system memory, it will hang the system or trigger the OOM killer.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00022.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00002.html
- https://usn.ubuntu.com/3606-1/
- http://www.securityfocus.com/bid/99977
- https://gist.github.com/dazhouzhou/1a3b7400547f23fe316db303ab9b604f
- https://www.debian.org/security/2018/dsa-4349
