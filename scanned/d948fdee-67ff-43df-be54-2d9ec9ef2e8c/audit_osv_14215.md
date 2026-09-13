# [H] CVE-2018-8007

## Summary
Severity: High
Advisory: CVE-2018-8007
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-11
Source: https://osv.dev/vulnerability/CVE-2018-8007
Type: osv

## Details
Apache CouchDB administrative users can configure the database server via HTTP(S). Due to insufficient validation of administrator-supplied configuration settings via the HTTP API, it is possible for a CouchDB administrator user to escalate their privileges to that of the operating system's user that CouchDB runs under, by bypassing the blacklist of configuration settings that are not allowed to be modified via the HTTP API. This privilege escalation effectively allows an existing CouchDB admin user to gain arbitrary remote code execution, bypassing already disclosed CVE-2017-12636. Mitigation: All users should upgrade to CouchDB releases 1.7.2 or 2.1.2.

## References
- http://mail-archives.apache.org/mod_mbox/couchdb-announce/201807.mbox/%3c1439409216.6221.1531246856676.JavaMail.Joan%40RITA%3e
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S5FPHVVU5KMRFKQTJPAM3TBGC7LKCWQS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X3JOUCX7LHDV4YWZDQNXT5NTKKRANZQW/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbmu03935en_us
- http://mail-archives.apache.org/mod_mbox/couchdb-announce/201807.mbox/%3C1699016538.6219.1531246785603.JavaMail.Joan%40RITA%3E
- http://www.securityfocus.com/bid/104741
- https://blog.couchdb.org/2018/07/10/cve-2018-8007/
- https://security.gentoo.org/glsa/201812-06
- https://www.mdsec.co.uk/2018/08/advisory-cve-2018-8007-apache-couchdb-remote-code-execution/
