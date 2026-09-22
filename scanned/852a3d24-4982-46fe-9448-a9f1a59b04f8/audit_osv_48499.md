# [H] CVE-2017-8779

## Summary
Severity: High
Advisory: CVE-2017-8779
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/CVE-2017-8779
Type: osv

## Details
rpcbind through 0.2.4, LIBTIRPC through 1.0.1 and 1.0.2-rc through 1.0.2-rc3, and NTIRPC through 1.4.3 do not consider the maximum RPC data size during memory allocation for XDR strings, which allows remote attackers to cause a denial of service (memory consumption with no subsequent free) via a crafted UDP packet to port 111, aka rpcbomb.

## References
- https://usn.ubuntu.com/3759-1/
- https://usn.ubuntu.com/3759-2/
- https://www.exploit-db.com/exploits/41974/
- http://www.securitytracker.com/id/1038532
- https://access.redhat.com/errata/RHSA-2017:1262
- https://access.redhat.com/errata/RHSA-2017:1267
- https://access.redhat.com/errata/RHSA-2017:1268
- https://security.gentoo.org/glsa/201706-07
- https://security.netapp.com/advisory/ntap-20180109-0001/
- http://www.debian.org/security/2017/dsa-3845
- https://access.redhat.com/errata/RHBA-2017:1497
- https://access.redhat.com/errata/RHSA-2017:1263
- http://www.securityfocus.com/bid/98325
- https://access.redhat.com/errata/RHSA-2017:1395
- https://guidovranken.wordpress.com/2017/05/03/rpcbomb-remote-rpcbind-denial-of-service-patches/
- https://github.com/drbothen/GO-RPCBOMB
- http://openwall.com/lists/oss-security/2017/05/03/12
- http://openwall.com/lists/oss-security/2017/05/04/1
- https://github.com/guidovranken/rpcbomb/
