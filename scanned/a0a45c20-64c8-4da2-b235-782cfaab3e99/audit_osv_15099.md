# [H] CVE-2019-13358

## Summary
Severity: High
Advisory: CVE-2019-13358
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13358
Type: osv

## Details
lib/DocumentToText.php in OpenCats before 0.9.4-3 has XXE that allows remote users to read files on the underlying operating system. The attacker must upload a file in the docx or odt format.

## References
- http://www.opencats.org/news/
- https://github.com/opencats/OpenCATS/pull/440
- http://packetstormsecurity.com/files/164253/OpenCats-0.9.4-2-XML-Injection.html
- https://doddsecurity.com/312/xml-external-entity-injection-xxe-in-opencats-applicant-tracking-system/
