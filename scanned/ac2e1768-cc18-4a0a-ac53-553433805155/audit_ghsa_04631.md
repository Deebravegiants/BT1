# [C] Langflow: BaseFileComponent-based nodes arbitrary file read with RCE exploit

## Summary
Severity: Critical
Advisory: GHSA-ccv6-r384-xp75
CVE: CVE-2026-55447
CWE: CWE-200, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-ccv6-r384-xp75
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.2

## Details
### Summary
All components based on `BaseFileComponent` are vulnerable to the following vulnerability:
1. Docling (`DoclingInlineComponent`)
2. Docling Serve (`DoclingRemoteComponent`)
3. Read File (`FileComponent`)
4. NVIDIA Retriever Extraction (`NvidiaIngestComponent`)
5. Video File (`VideoFileComponent`)
6. Unstructured API (`UnstructuredComponent`)

For clarity, from now on I'll only refer to Read File component.

The Read File node processes user-controlled files.
Example scenario is a RAG chatbot - a system that allows users of an organization to ask questions about documents saved in the organizations.

By controlling a files that are digested into the RAG, an attacker can direct the node to read *any* file on the file-system by absolute path.

Using this vulnerability an attacker can acheive RCE:
1. Upload a file that directs the node to read Langflow's `secret_key` file containing the JWT token secret.
2. This would allow the attacker then to simply task the Chatbot for the JWT secret.
3. Using this secret, the attacker then crafts a JWT token for any user-id, bypassing authentication.
4. Code execution is then trivial - simply create a new flow with "Python Interpreter" node, fill it with arbitrary Python code and execute it.

Tested on commit 2d67402b1dbaefcbce85a244d4a6cd5e4bda1cfe

### Details
The vulnerability is in:
`langflow/src/lfx/src/lfx/base/data/base_file.py`
Specifically in `_unpack_bundle`. This function extracts tar files, which can contain a symlink.
This symlink can point to any file in the filesystem. Then, in `self.process_files()`, the file pointed by the symlink will be parsed and saved into the RAG.
This can be done with unlimited number of symlinks in the same tar which can also be useful in some scenarios.

Suggestd fix - iterate over the files and make sure all are regular files or directories.


### PoC
Reproduction:
1. Create a flow with Read File (or any other affected components), and connect its output to some storage such as Chroma DB.
2. Create a symlink pointing to any file. For the above exploit, point the symlink to langflow's JWT token file.
3. Compress this symlink with tar.
4. Upload it to the Read File component.
5. Check the database, or ask a Chatbot connected to this vector database for the contents of the file.


Concrete PoC:
------------

- Flow with RAG ingestion and a Chatbot around it: [Vector Store RAG.json](https://github.com/user-attachments/files/25159960/Vector.Store.RAG.json)
- Exploit tar: [archive.tar.txt](https://github.com/user-attachments/files/25159954/archive.tar.txt) (remove .txt, GitHub blocked .tar)
- Create a file `/tmp/trip.docx` with any contents in it
- Ingest the file in the flow above, and ask the Chatbot a question about this file.

A demo showing the attack:
https://github.com/user-attachments/assets/af00f700-f13f-4eac-848e-8afd11fb9297
In the demo the attacker steals `Langflow` secret key used to sign JWTs. The second stage of the attack, not shown in the demo, is using this key to sign a JWT token and executing Python code on the server using the Python code interpreter node.

### Impact
Any Langflow user using any of the above mentioned components to ingest user-controlled data is affected. Depending on exact scenario, the user can also be exposed to an RCE risk.


### Patches
Fixed in **1.9.2** via PR [#12945](https://github.com/langflow-ai/langflow/pull/12945). `BaseFileComponent._unpack_bundle` now rejects symlink and hardlink members (and any non-regular entries) during TAR extraction, with additional defensive symlink filtering during directory recursion and after extraction. Upgrade to **1.9.2 or later**.


Ori Lahav
Security Researcher @ Rubrik Inc.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-ccv6-r384-xp75
- https://github.com/langflow-ai/langflow/pull/12945
- https://github.com/langflow-ai/langflow
