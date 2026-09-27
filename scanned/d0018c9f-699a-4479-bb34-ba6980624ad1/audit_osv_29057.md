# [M] SkillTree CSRF Vulnerability allows an attacker to modify the Video and Captions of a Skill

## Summary
Severity: Medium
Advisory: CVE-2024-39326
Aliases: GHSA-9624-qwxr-jr4j
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-07-02
Source: https://osv.dev/vulnerability/CVE-2024-39326
Type: osv

## Details
SkillTree is a micro-learning gamification platform. Prior to version 2.12.6, the endpoint 
`/admin/projects/{projectname}/skills/{skillname}/video` (and probably others) is open to a cross-site request forgery (CSRF) vulnerability. Due to the endpoint being CSRFable e.g POST request, supports a content type that can be exploited (multipart file upload), makes a state change and has no CSRF mitigations in place (samesite flag, CSRF token). It is possible to perform a CSRF attack against a logged in admin account, allowing an attacker that can target a logged in admin of Skills Service to modify the videos, captions, and text of the skill. Version 2.12.6 contains a patch for this issue.

## References
- https://github.com/NationalSecurityAgency/skills-service/blob/24dd22f43306fc616e4580fb8bb88f66b5d9b41d/service/src/main/java/skills/controller/AdminController.groovy#L574
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39326.json
- https://github.com/NationalSecurityAgency/skills-service/security/advisories/GHSA-9624-qwxr-jr4j
- https://nvd.nist.gov/vuln/detail/CVE-2024-39326
- https://github.com/NationalSecurityAgency/skills-service/commit/68d4235ddcb16e4f33fc7f19d14ff917817a366c
