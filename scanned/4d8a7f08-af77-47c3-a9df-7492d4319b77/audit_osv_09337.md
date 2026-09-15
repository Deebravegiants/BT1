# [C] CVE-2016-9481

## Summary
Severity: Critical
Advisory: CVE-2016-9481
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-29
Source: https://osv.dev/vulnerability/CVE-2016-9481
Type: osv

## Details
In framework/modules/core/controllers/expCommentController.php of Exponent CMS 2.4.0, content_id input is passed into showComments. The method showComments is defined in the expCommentControllercontroller with the parameter '$this->params['content_id']' used directly in SQL. Impact is a SQL injection.

## References
- http://www.securityfocus.com/bid/94590
- http://www.securitytracker.com/id/1037368
- http://www.pang0lin.com/?p=1076
