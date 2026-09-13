# [M] CVE-2015-8346

## Summary
Severity: Medium
Advisory: CVE-2015-8346
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2015-8346
Type: osv

## Details
app/views/timelog/_form.html.erb in Redmine before 2.6.8, 3.0.x before 3.0.6, and 3.1.x before 3.1.2 allows remote attackers to obtain sensitive information about subjects of issues by viewing the time logging form.

## References
- http://www.debian.org/security/2016/dsa-3529
- http://www.redmine.org/news/102
- http://www.redmine.org/news/102
- https://github.com/redmine/redmine/commit/c096dde88ff02872ba35edc4dc403c80a7867b5c
- https://www.redmine.org/issues/21150
