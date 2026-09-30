# [C] CVE-2019-6713

## Summary
Severity: Critical
Advisory: CVE-2019-6713
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-23
Source: https://osv.dev/vulnerability/CVE-2019-6713
Type: osv

## Details
app\admin\controller\RouteController.php in ThinkCMF 5.0.190111 allows remote attackers to execute arbitrary PHP code by using vectors involving portal/List/index and list/:id to inject this code into data\conf\route.php, as demonstrated by a file_put_contents call.

## References
- https://www.thinkcmf.com/download.html
- http://www.ttk7.cn/post-108.html
