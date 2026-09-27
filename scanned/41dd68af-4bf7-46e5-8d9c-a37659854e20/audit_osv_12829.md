# [C] CVE-2018-15474

## Summary
Severity: Critical
Advisory: CVE-2018-15474
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-09-07
Source: https://osv.dev/vulnerability/CVE-2018-15474
Type: osv

## Details
CSV Injection (aka Excel Macro Injection or Formula Injection) in /lib/plugins/usermanager/admin.php in DokuWiki 2018-04-22a and earlier allows remote attackers to exfiltrate sensitive data and to execute arbitrary code via a value that is mishandled in a CSV export.  NOTE: the vendor has stated "this is not a security problem in DokuWiki.

## References
- https://www.patreon.com/posts/unfixed-security-21250652
- https://github.com/splitbrain/dokuwiki/issues/2450
- https://seclists.org/fulldisclosure/2018/Sep/4
- https://www.sec-consult.com/en/blog/advisories/dokuwiki-csv-formula-injection-vulnerability/
