# [C] ILIAS PHP Object Injection via Shibboleth Logout

## Summary
Severity: Critical
Advisory: CVE-2026-80428
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80428
Type: osv

## Details
ILIAS before versions 9.22, 10.10, and 11.3 contains an unauthenticated PHP object injection vulnerability that allows unauthenticated attackers to execute arbitrary code by injecting serialized objects through the LTI authentication endpoint and triggering deserialization via the Shibboleth back-channel logout endpoint. Attackers can write arbitrary serialized objects into session storage, then exploit an available POP gadget through the logout endpoint's unrestricted deserialization to write attacker-controlled PHP content to a web-accessible path and achieve remote code execution as the web server user.

## References
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=934
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=935
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=936
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80428.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80428
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225630&ref_id=35
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225631&ref_id=35
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225632&ref_id=35
- https://github.com/ILIAS-eLearning/ILIAS
