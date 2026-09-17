# [H] CVE-2019-9199

## Summary
Severity: High
Advisory: CVE-2019-9199
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2019-9199
Type: osv

## Details
PoDoFo::Impose::PdfTranslator::setSource() in pdftranslator.cpp in PoDoFo 0.9.6 has a NULL pointer dereference that can (for example) be triggered by sending a crafted PDF file to the podofoimpose binary. It allows an attacker to cause Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CIC2EXSSMBT3MY2HY42IIY4BUQS2SVYB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NTJ5AAM6Y4NMSELEH7N5ZG4DNO56BCYF/
- https://github.com/jjanku/podofo/commit/ada821df68fb0bf673840ed525daf4ec709dbfd9
- https://github.com/mksdev/podofo/commit/1400a9aaf611299b9a56aa2abeb158918b9743c8
- https://research.loginsoft.com/bugs/null-pointer-dereference-vulnerability-in-setsource-podofo-0-9-6-trunk-r1967/
- https://sourceforge.net/p/podofo/tickets/40/
