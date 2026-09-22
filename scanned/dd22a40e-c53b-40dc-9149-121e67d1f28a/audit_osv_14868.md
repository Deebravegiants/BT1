# [H] CVE-2019-12098

## Summary
Severity: High
Advisory: CVE-2019-12098
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-12098
Type: osv

## Details
In the client side of Heimdal before 7.6.0, failure to verify anonymous PKINIT PA-PKINIT-KX key exchange permits a man-in-the-middle attack. This issue is in krb5_init_creds_step in lib/krb5/init_creds_pw.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GIXEDVVMPD6ZAJSMI2EZ7FNEIVNWE5PD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SLXXIF4LOQEAEDAF4UGP2AO6WDNTDFUB/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00026.html
- https://github.com/heimdal/heimdal/releases/tag/heimdal-7.6.0
- https://seclists.org/bugtraq/2019/Jun/1
- https://www.debian.org/security/2019/dsa-4455
- http://www.h5l.org/pipermail/heimdal-announce/2019-May/000009.html
- https://github.com/heimdal/heimdal/commit/2f7f3d9960aa6ea21358bdf3687cee5149aa35cf
- https://github.com/heimdal/heimdal/compare/3e58559...bbafe72
