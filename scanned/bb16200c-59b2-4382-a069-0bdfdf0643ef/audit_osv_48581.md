# [H] CVE-2017-9765

## Summary
Severity: High
Advisory: CVE-2017-9765
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-20
Source: https://osv.dev/vulnerability/CVE-2017-9765
Type: osv

## Details
Integer overflow in the soap_get function in Genivia gSOAP 2.7.x and 2.8.x before 2.8.48, as used on Axis cameras and other devices, allows remote attackers to execute arbitrary code or cause a denial of service (stack-based buffer overflow and application crash) via a large XML document, aka Devil's Ivy. NOTE: the large document would be blocked by many common web-server configurations on general-purpose computers.

## References
- https://www.genivia.com/advisory.html#Security_advisory:_CVE-2017-9765_bug_in_certain_versions_of_gSOAP_2.7_up_to_2.8.47_%28June_21%2C_2017%29
- https://www.genivia.com/changelog.html#Version_2.8.48_upd_%2806/21/2017%29
- http://blog.senr.io/blog/devils-ivy-flaw-in-widely-used-third-party-code-impacts-millions
- http://www.securityfocus.com/bid/99868
- https://bugzilla.redhat.com/show_bug.cgi?id=1472807
- https://bugzilla.suse.com/show_bug.cgi?id=1049348
- http://blog.senr.io/devilsivy.html
