# [H] CVE-2017-7694

## Summary
Severity: High
Advisory: CVE-2017-7694
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2017-7694
Type: osv

## Details
Remote Code Execution vulnerability in symphony/content/content.blueprintsdatasources.php in Symphony CMS through 2.6.11 allows remote attackers to execute code and get a webshell from the back-end. The attacker must be authenticated and enter PHP code in the datasource editor or event editor.

## References
- http://www.securityfocus.com/bid/97594
- https://github.com/symphonycms/symphony-2/commit/e30a18f8f09dca836e141bf126a26e565c9a2bc7
- https://github.com/symphonycms/symphony-2/issues/2655
- http://www.math1as.com/symphonycms_2.7_exec.txt
