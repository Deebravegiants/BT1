# [H] CVE-2017-12636

## Summary
Severity: High
Advisory: CVE-2017-12636
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-14
Source: https://osv.dev/vulnerability/CVE-2017-12636
Type: osv

## Details
CouchDB administrative users can configure the database server via HTTP(S). Some of the configuration options include paths for operating system-level binaries that are subsequently launched by CouchDB. This allows an admin user in Apache CouchDB before 1.7.0 and 2.x before 2.1.1 to execute arbitrary shell commands as the CouchDB user, including downloading and executing scripts from the public internet.

## References
- https://lists.apache.org/thread.html/6c405bf3f8358e6314076be9f48c89a2e0ddf00539906291ebdf0c67%40%3Cdev.couchdb.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/01/msg00026.html
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbmu03935en_us
- https://www.exploit-db.com/exploits/44913/
- https://www.exploit-db.com/exploits/45019/
- https://security.gentoo.org/glsa/201711-16
