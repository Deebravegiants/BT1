# [H] CVE-2016-8742

## Summary
Severity: High
Advisory: CVE-2016-8742
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2016-8742
Type: osv

## Details
The Windows installer that the Apache CouchDB team provides was vulnerable to local privilege escalation. All files in the install inherit the file permissions of the parent directory and therefore a non-privileged user can substitute any executable for the nssm.exe service launcher, or CouchDB batch or binary files. A subsequent service or server restart will then run that binary with administrator privilege. This issue affected CouchDB 2.0.0 (Windows platform only) and was addressed in CouchDB 2.0.0.1.

## References
- http://mail-archives.apache.org/mod_mbox/couchdb-dev/201612.mbox/%3C825F65E1-0E5F-4E1F-8053-CF2C6200C526%40apache.org%3E
- http://www.securityfocus.com/bid/94766
- https://www.exploit-db.com/exploits/40865/
