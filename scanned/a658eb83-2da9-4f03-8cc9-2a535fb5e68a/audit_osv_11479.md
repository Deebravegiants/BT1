# [C] CVE-2017-7991

## Summary
Severity: Critical
Advisory: CVE-2017-7991
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-22
Source: https://osv.dev/vulnerability/CVE-2017-7991
Type: osv

## Details
Exponent CMS 2.4.1 and earlier has SQL injection via a base64 serialized API key (apikey parameter) in the api function of framework/modules/eaas/controllers/eaasController.php.

## References
- https://github.com/exponentcms/exponent-cms/commit/67a9c2f0229de120431f3eecb0f5017075517105
- http://seclists.org/fulldisclosure/2017/Apr/78
- https://gist.github.com/404notf0und/ab59234d71fbf35b4926ffd646324f29
- https://packetstormsecurity.com/files/142258/Exponent-CMS-2.4.1-SQL-Injection.html
