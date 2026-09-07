# [M] NocoDB Allows Preview of Files with Dangerous Content

## Summary
Severity: Medium
Advisory: GHSA-qg73-g3cf-vhhh
CVE: CVE-2023-50717
CWE: CWE-434, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-qg73-g3cf-vhhh
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0.202.6 <0.202.10

## Details
### Summary
---
Attacker can upload a html file with malicious content. If user tries to open that file in browser malicious scripts can be executed leading  Stored XSS(Cross-Site Script) attack.

### PoC
---
NocoDB was configured using the Release Binary `Noco-macos-arm64`, and nocodb version 0.202.9 (currently the latest version) was used.
binary hash infos: md5(164b727f287af56168bc16fba622d0b4) / sha256(43e8e97f4c5f5330613abe071a359f84e4514b7186f92954b678087c37b7832e)
<img width="665" alt="image" src="https://user-images.githubusercontent.com/86613161/287472673-aeb60a02-2080-429f-8583-9f130ab62779.png">

### 1. Run the binary to start the server and access the arbitrary table dashboard.
<img width="830" alt="image" src="https://user-images.githubusercontent.com/86613161/287472852-98b2286e-ad66-45bf-b503-63780619d775.png">

Here, used the default `Features` table.

### 2. Click `+` in the table `field header` to add an `attachment` field.
<img width="1173" alt="image" src="https://user-images.githubusercontent.com/86613161/287472936-98a67213-a547-4e71-915c-d2a43300530b.png">

### 3. Click the `Add File(s)` button to select and upload files.

<img width="1132" alt="image" src="https://user-images.githubusercontent.com/86613161/287473041-0801ff39-e48c-4746-8518-be825bfd5533.png">

Here, `test.html` containing `<script>alert(document.domain)</script>` was uploaded.

### 4. Check the uploaded file path.
<img width="1163" alt="image" src="https://user-images.githubusercontent.com/86613161/287473337-b1c7c781-2fb5-4bd0-b464-dbd3d4158f04.png"

### 5. Access the uploaded file path.
<img width="1201" alt="image" src="https://user-images.githubusercontent.com/86613161/287473278-410f9228-58e3-4ee4-b111-70cdbffa9ed5.png">

When the file path is accessed, the `<script>alert(document.domain)</script>` script statement contained in the file is executed and the server host appears in the alert message.


### Impact
---
This allows remote attacker to execute JavaScript code in the context of the user accessing the vector. An attacker could have used this vulnerability to execute requests in the name of a logged-in user or potentially collect information about the attacked user by displaying a malicious form.

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-qg73-g3cf-vhhh
- https://nvd.nist.gov/vuln/detail/CVE-2023-50717
- https://github.com/nocodb/nocodb
