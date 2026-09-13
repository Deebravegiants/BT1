# [M] Server-Side Request Forgery and Local File Disclosure in CTI-Transmute Evaluation PDF Rendering

## Summary
Severity: Medium
Advisory: CVE-2026-69078
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69078
Type: osv

## Details
CTI-Transmute is affected by a server-side request forgery vulnerability in the evaluation report PDF-generation functionality.

User-controlled CTI content, including conversion names, descriptions, and comments, is converted from Markdown to HTML and rendered as a PDF using WeasyPrint. Before the patch, the renderer used WeasyPrint’s default URL-fetching behavior without restricting the protocols or destinations that could be referenced by the generated HTML.

An attacker able to supply content included in an evaluation report could inject crafted resource references using schemes such as http://, https://, or file://. When the report was rendered, CTI-Transmute could fetch these resources using the application server’s network connectivity and filesystem privileges.

Successful exploitation could allow an attacker to:

  *  access services available only from the CTI-Transmute server or its internal network;
  *  probe internal hosts and service endpoints;
  *  retrieve local files readable by the application process; and
  *  expose fetched content through the generated PDF, depending on the referenced resource type and rendering context.


The vulnerability is corrected by providing WeasyPrint with a restrictive URL fetcher that permits only self-contained data: URIs. The externally hosted Google Fonts stylesheet was also removed so that PDF generation performs no intentional network or filesystem fetches.

## References
- https://github.com/MISP/cti-transmute/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69078.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69078
- https://github.com/MISP/cti-transmute/commit/20f35307bcb706c8dd8ca3884a88fb36b05b5244
