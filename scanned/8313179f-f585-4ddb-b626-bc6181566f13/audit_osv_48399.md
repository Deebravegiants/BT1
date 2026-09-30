# [H] CVE-2017-7308

## Summary
Severity: High
Advisory: CVE-2017-7308
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7308
Type: osv

## Details
The packet_set_ring function in net/packet/af_packet.c in the Linux kernel through 4.10.6 does not properly validate certain block-size data, which allows local users to cause a denial of service (integer signedness error and out-of-bounds write), or gain privileges (if the CAP_NET_RAW capability is held), via crafted system calls.

## References
- https://www.exploit-db.com/exploits/41994/
- https://www.exploit-db.com/exploits/44654/
- http://www.securityfocus.com/bid/97234
- https://access.redhat.com/errata/RHSA-2018:1854
- https://patchwork.ozlabs.org/patch/744811/
- https://patchwork.ozlabs.org/patch/744812/
- https://source.android.com/security/bulletin/2017-07-01
- https://access.redhat.com/errata/RHSA-2017:1297
- https://access.redhat.com/errata/RHSA-2017:1298
- https://access.redhat.com/errata/RHSA-2017:1308
- https://googleprojectzero.blogspot.com/2017/05/exploiting-linux-kernel-via-packet.html
- https://patchwork.ozlabs.org/patch/744813/
