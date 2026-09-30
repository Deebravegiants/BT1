# [H] CVE-2018-1299

## Summary
Severity: High
Advisory: CVE-2018-1299
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2018-1299
Type: osv

## Details
In Apache Allura before 1.8.0, unauthenticated attackers may retrieve arbitrary files through the Allura web application. Some webservers used with Allura, such as Nginx, Apache/mod_wsgi or paster may prevent the attack from succeeding. Others, such as gunicorn do not prevent it and leave Allura vulnerable.

## References
- https://lists.apache.org/thread.html/b52069073cf3cb0f84c9e1e2b34d411fc163af39e4f3e50712ac8a4d%40%3Cdev.allura.apache.org%3E
- https://allura.apache.org/posts/2018-allura-1.8.0.html
