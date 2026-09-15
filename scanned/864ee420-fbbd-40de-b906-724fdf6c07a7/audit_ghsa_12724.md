# [C]  MITM based Zip Slip in `org.hl7.fhir.publisher:org.hl7.fhir.publisher`

## Summary
Severity: Critical
Advisory: GHSA-xr8x-pxm6-prjg
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-23
Source: https://github.com/advisories/GHSA-xr8x-pxm6-prjg
Type: github-advisory

## Affected
- Maven: `org.hl7.fhir.publisher:org.hl7.fhir.publisher` — affected >=0 <1.2.30

## Details
### Impact
MITM can enable Zip-Slip.

### Vulnerability

#### Vulnerability 1: `Publisher.java`

There is no validation that the zip file being unpacked has entries that are not maliciously writing outside of the intended destination directory.

https://github.com/HL7/fhir-ig-publisher/blob/87313e92de6dd6cea816449e0edd225e054a7891/org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/Publisher.java#L3598-L3610

#### Vulnerability 2: `WebSourceProvider.java`

There is a check for malicious zip entries here, but it is not covered by test cases and could potentially be reverted in future changes.

https://github.com/HL7/fhir-ig-publisher/blob/87313e92de6dd6cea816449e0edd225e054a7891/org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/web/WebSourceProvider.java#L104-L112

#### Vulnerability 3: `ZipFetcher.java`

This retains the path for Zip files in FetchedFile entries, which could later be used to output malicious entries to another compressed file or file system.

https://github.com/HL7/fhir-ig-publisher/blob/87313e92de6dd6cea816449e0edd225e054a7891/org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/ZipFetcher.java#L57-L106

#### Vulnerability 4: `IGPack2NpmConvertor.java`

The loadZip method retains the path for entries in the zip file, which could later be used to output malicious entries to another compressed file or file system.

https://github.com/HL7/fhir-ig-publisher/blob/87313e92de6dd6cea816449e0edd225e054a7891/org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/IGPack2NpmConvertor.java#L442-L463

## References
- https://github.com/HL7/fhir-ig-publisher/security/advisories/GHSA-xr8x-pxm6-prjg
- https://github.com/HL7/fhir-ig-publisher
