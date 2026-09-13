# [H] CVE-2014-1235

## Summary
Severity: High
Advisory: CVE-2014-1235
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2014-1235
Type: osv

## Details
Stack-based buffer overflow in the "yyerror" function in Graphviz 2.34.0 allows remote attackers to execute arbitrary code or cause a denial of service (application crash) via a crafted file.  NOTE: This vulnerability exists due to an incomplete fix for CVE-2014-0978.

## References
- http://seclists.org/oss-sec/2014/q1/54
- http://www.securityfocus.com/bid/64736
- https://bugzilla.redhat.com/show_bug.cgi?id=1050871
- https://github.com/ellson/graphviz/commit/d266bb2b4154d11c27252b56d86963aef4434750
- https://security.gentoo.org/glsa/201702-06
- http://seclists.org/oss-sec/2014/q1/54
- https://bugzilla.redhat.com/show_bug.cgi?id=1050871
- https://github.com/ellson/graphviz/commit/d266bb2b4154d11c27252b56d86963aef4434750
- https://security.gentoo.org/glsa/201702-06
- https://bugzilla.redhat.com/show_bug.cgi?id=1050871
- https://github.com/ellson/graphviz/commit/d266bb2b4154d11c27252b56d86963aef4434750
- https://exchange.xforce.ibmcloud.com/vulnerabilities/90198
