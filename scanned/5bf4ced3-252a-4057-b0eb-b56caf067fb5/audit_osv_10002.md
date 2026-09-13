# [C] CVE-2017-12635

## Summary
Severity: Critical
Advisory: CVE-2017-12635
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-14
Source: https://osv.dev/vulnerability/CVE-2017-12635
Type: osv

## Details
Due to differences in the Erlang-based JSON parser and JavaScript-based JSON parser, it is possible in Apache CouchDB before 1.7.0 and 2.x before 2.1.1 to submit _users documents with duplicate keys for 'roles' used for access control within the database, including the special case '_admin' role, that denotes administrative users. In combination with CVE-2017-12636 (Remote Code Execution), this can be used to give non-admin users access to arbitrary shell commands on the server as the database system user. The JSON parser differences result in behaviour that if two 'roles' keys are available in the JSON, the second one will be used for authorising the document write, but the first 'roles' key is used for subsequent authorization for the newly created user. By design, users can not assign themselves roles. The vulnerability allows non-admin users to give themselves admin privileges.

## References
- https://lists.apache.org/thread.html/6c405bf3f8358e6314076be9f48c89a2e0ddf00539906291ebdf0c67%40%3Cdev.couchdb.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/01/msg00026.html
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbmu03935en_us
- https://www.exploit-db.com/exploits/44498/
- https://www.exploit-db.com/exploits/45019/
- http://www.securityfocus.com/bid/101868
- https://security.gentoo.org/glsa/201711-16
