# [H] CVE-2017-8291

## Summary
Severity: High
Advisory: CVE-2017-8291
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8291
Type: osv

## Details
Artifex Ghostscript through 2017-04-26 allows -dSAFER bypass and remote command execution via .rsdparams type confusion with a "/OutputFile (%pipe%" substring in a crafted .eps document that is an input to the gs program, as exploited in the wild in April 2017.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-8291
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=04b37bbce174eed24edec7ad5b920eb93db4d47d
- http://www.debian.org/security/2017/dsa-3838
- https://security.gentoo.org/glsa/201708-06
- http://www.securityfocus.com/bid/98476
- https://access.redhat.com/errata/RHSA-2017:1230
- https://bugzilla.suse.com/show_bug.cgi?id=1036453
- https://bugs.ghostscript.com/show_bug.cgi?id=697808
- http://openwall.com/lists/oss-security/2017/04/28/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1446063
- https://www.exploit-db.com/exploits/41955/
