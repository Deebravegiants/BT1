# [H] pyLoad is vulnerable to attacks that bypass localhost restrictions, enabling the creation of arbitrary packages

## Summary
Severity: High
Advisory: GHSA-x698-5hjm-w2m5
CVE: CVE-2025-7346
CWE: CWE-284, CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-07-08
Source: https://github.com/advisories/GHSA-x698-5hjm-w2m5
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
### Summary
Any unauthenticated attacker can bypass the localhost restrictions posed by the application and utilize this to create arbitrary packages.

### Details
Any unauthenticated attacker can bypass the localhost restrictions posed by the application and utilize this to create arbitrary packages. This is done by changing the `Host` header to the value of `127.0.0.1:9666`.

### PoC
The application has middleware that prevents access to several routes by checking whether the `Host` header has a specific value. We bypassed this restriction.

https://github.com/pyload/pyload/blob/4159a1191ec4fe6d927e57a9c4bb8f54e16c381d/src/pyload/webui/app/blueprints/cnl_blueprint.py#L21-L36
```python
#: decorator
def local_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        remote_addr = flask.request.environ.get("REMOTE_ADDR", "0")
        http_host = flask.request.environ.get("HTTP_HOST", "0")

        if remote_addr in ("127.0.0.1", "::ffff:127.0.0.1", "::1", "localhost") or http_host in (
            "127.0.0.1:9666",
            "[::1]:9666",
        ):
            return func(*args, **kwargs)
        else:
            return "Forbidden", 403

    return wrapper
```

Below we see that the '/flash/add' endpoint uses the middleware above.

https://github.com/pyload/pyload/blob/4159a1191ec4fe6d927e57a9c4bb8f54e16c381d/src/pyload/webui/app/blueprints/cnl_blueprint.py#L56-L58C11
```python
@bp.route("/flash/add", methods=["POST"], endpoint="add")
@local_check
def add():
```

Notice how we are not authorized to access this endpoint when sending a request.
![image](https://user-images.githubusercontent.com/44903767/294935526-64217d91-c0d1-4d8f-963f-cedfa8dc9034.png)

However, if we set the `Host` header to be `127.0.0.1:9666`, we notice the request returns `success`.
![image](https://user-images.githubusercontent.com/44903767/294933755-43ad3826-0e94-4ba5-acf0-48f11670cbc6.png)

Checking the front end as an admin, we now see that this did indeed succeed.
![image](https://user-images.githubusercontent.com/44903767/294934431-5d024c75-59dc-47b6-8887-b14ae91e320f.png)

### Impact
An unauthenticated user can perform actions that should only be available to authenticated users.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-x698-5hjm-w2m5
- https://github.com/pyload/pyload/commit/f4e2d12416ba2dfac7b036d5c8d6dab5461b9840
- https://github.com/pyload/pyload
- https://github.com/pyload/pyload/blob/4159a1191ec4fe6d927e57a9c4bb8f54e16c381d/src/pyload/webui/app/blueprints/cnl_blueprint.py#L21-L36
- https://github.com/pyload/pyload/blob/4159a1191ec4fe6d927e57a9c4bb8f54e16c381d/src/pyload/webui/app/blueprints/cnl_blueprint.py#L56-L58C11
