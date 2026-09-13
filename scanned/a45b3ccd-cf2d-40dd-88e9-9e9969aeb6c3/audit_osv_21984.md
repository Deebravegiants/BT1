# [M] Information Exposure

## Summary
Severity: Medium
Advisory: CVE-2022-21230
Aliases: GHSA-2r85-x9cf-8fcg, SNYK-JAVA-ORGNANOHTTPD-2422798
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-01
Source: https://osv.dev/vulnerability/CVE-2022-21230
Type: osv

## Details
This affects all versions of package org.nanohttpd:nanohttpd. Whenever an HTTP Session is parsing the body of an HTTP request, the body of the request is written to a RandomAccessFile when the it is larger than 1024 bytes. This file is created with insecure permissions that allow its contents to be viewed by all users on the host machine. **Workaround:** Manually specifying the -Djava.io.tmpdir= argument when launching Java to set the temporary directory to a directory exclusively controlled by the current user can fix this issue.

## References
- https://github.com/NanoHttpd/nanohttpd/blob/efb2ebf85a2b06f7c508aba9eaad5377e3a01e81/core/src/main/java/org/nanohttpd/protocols/http/tempfiles/DefaultTempFile.java%23L58
- https://github.com/NanoHttpd/nanohttpd/blob/efb2ebf85a2b06f7c508aba9eaad5377e3a01e81/core/src/main/java/org/nanohttpd/protocols/http/tempfiles/DefaultTempFileManager.java%23L60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21230.json
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-2r85-x9cf-8fcg
- https://nvd.nist.gov/vuln/detail/CVE-2022-21230
- https://snyk.io/vuln/SNYK-JAVA-ORGNANOHTTPD-2422798
