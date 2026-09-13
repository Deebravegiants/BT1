# [C] CVE-2026-8711

## Summary
Severity: Critical
Advisory: CVE-2026-8711
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-8711
Type: osv

## Details
NGINX JavaScript has a vulnerability when the js_fetch_proxy directive is configured with at least one client-controlled NGINX variable (for example, $http_*, $arg_*, $cookie_*) and a location invoking the ngx.fetch() operation from NGINX JavaScript. An unauthenticated attacker can exploit this vulnerability by sending crafted HTTP requests. This may cause a heap buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161307
