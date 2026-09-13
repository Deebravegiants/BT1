# [C] CVE-2020-1693

## Summary
Severity: Critical
Advisory: CVE-2020-1693
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-17
Source: https://osv.dev/vulnerability/CVE-2020-1693
Type: osv

## Details
A flaw was found in Spacewalk up to version 2.9 where it was vulnerable to XML internal entity attacks via the /rpc/api endpoint. An unauthenticated remote attacker could use this flaw to retrieve the content of certain files and trigger a denial of service, or in certain circumstances, execute arbitrary code on the Spacewalk server.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1693
- https://github.com/spacewalkproject/spacewalk/commit/74e28ec61d916c42061ef4347121650a1c962b0c
- https://zeroauth.ltd/blog/2020/02/18/proof-of-concept-exploit-for-cve-2020-1693-spacewalk/
