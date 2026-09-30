# [M] Denial of Service in MISP-STIX Import via Malformed or Oversized STIX Documents in misp-stix library

## Summary
Severity: Medium
Advisory: CVE-2026-77755
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77755
Type: osv

## Details
A denial-of-service vulnerability was identified in misp-stix when processing attacker-controlled STIX 1 or STIX 2 documents.

The STIX import code used sys.exit() to handle several parsing and loading failures. Because SystemExit inherits from BaseException rather than Exception, these failures bypassed the exception handlers used by callers of the library. As a result, a malformed STIX document could terminate a long-running importer process instead of returning a recoverable parsing error.

Additionally, no limit was imposed on the size of STIX documents before parsing. A submitted document was therefore read and materialised in memory before its validity or type was evaluated. Depending on the document and parsing path, processing could consume approximately two to seven times the input size in memory, allowing a sufficiently large STIX document to cause excessive memory and CPU consumption and potentially terminate or severely degrade the importing service.

An attacker able to provide STIX content to a MISP-STIX import workflow could exploit either condition to affect availability. A malformed document could cause abnormal process termination through an uncaught SystemExit, while a large document could exhaust resources during deserialisation and conversion.

The fixes replace process-terminating sys.exit() calls with catchable exceptions such as STIXLoadingError and MissingSTIXContentError, and extend exception handling around the complete STIX detection and conversion process. The importer also now enforces an input-size limit before parsing. The default maximum is 100 MB, can be adjusted by callers, and can explicitly be disabled when required. STIX 1 inputs are additionally checked for the expected root element before the complete XML tree is constructed.

ImpactSuccessful exploitation can cause:

  *  termination of a long-running MISP-STIX importer;
  *  excessive memory allocation;
  *  excessive CPU consumption;
  *  degradation or temporary unavailability of services relying on the converter;
  *  interruption of batch or automated STIX ingestion workflows.

## References
- https://github.com/MISP/misp-stix/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77755.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77755
- https://github.com/MISP/misp-stix/commit/66119552
- https://github.com/MISP/misp-stix/commit/e8e732ad
