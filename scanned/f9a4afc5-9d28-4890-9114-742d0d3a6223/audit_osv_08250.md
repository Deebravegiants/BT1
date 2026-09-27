# [M] CVE-2016-1907

## Summary
Severity: Medium
Advisory: CVE-2016-1907
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-01-19
Source: https://osv.dev/vulnerability/CVE-2016-1907
Type: osv

## Details
The ssh_packet_read_poll2 function in packet.c in OpenSSH before 7.1p2 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via crafted network traffic.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176516.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175676.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176349.html
- http://www.securityfocus.com/bid/81293
- https://anongit.mindrot.org/openssh.git/commit/?id=2fecfd486bdba9f51b3a789277bb0733ca36e1c0
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05356388
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05385680
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- http://www.openssh.com/txt/release-7.1p2
- https://bto.bluecoat.com/security-advisory/sa109
