# [H] pyload Unauthenticated Flask Configuration Leakage vulnerability

## Summary
Severity: High
Advisory: GHSA-mqpq-2p68-46fv
CVE: CVE-2024-21644
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-08
Source: https://github.com/advisories/GHSA-mqpq-2p68-46fv
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev77

## Details
### Summary
Any unauthenticated user can browse to a specific URL to expose the Flask config, including the `SECRET_KEY` variable.

### Details
Any unauthenticated user can browse to a specific URL to expose the Flask config, including the `SECRET_KEY` variable.

### PoC
Run `pyload` in the default configuration by running the following command
```
pyload
```

Now browse to `http://localhost:8000/render/info.html`. Notice how the Flask configuration gets displayed.
![PoC](https://user-images.githubusercontent.com/44903767/294522246-4cc19c49-b315-4926-8fd6-ec3c3fdb7c1f.png)

I was quite amused by this finding. I think it's a very interesting coming together of things that is so unlikely to happen. Below I will detail my process a bit more.

I was looking through the code to see how the authorization mechanism is implemented when I spotted this route, which can be accessed by any unauthenticated actor
- https://github.com/pyload/pyload/blob/57d81930edb59177c60830ad8ac36a91d0ec4c4e/src/pyload/webui/app/blueprints/app_blueprint.py#L33C1-L37C51
```python
@bp.route("/render/<path:filename>", endpoint="render")
def render(filename):
    mimetype = mimetypes.guess_type(filename)[0] or "text/html"
    data = render_template(filename)
    return flask.Response(data, mimetype=mimetype)
 ```

This route allows me to load in any of the predefined templates. However, these templates will be lacking any form of context, and as such it doesn't seem too useful. That is until I loaded the `info.html` template and scrolled down, revealing the Flask config. This was purely accidental, and I did not understand why it happened, until I looked at the template

- https://github.com/pyload/pyload/blob/57d81930edb59177c60830ad8ac36a91d0ec4c4e/src/pyload/webui/app/templates/info.html#L64C1-L67C10
```python
    <tr>
        <td>{{ _("Config folder:") }}</td>
        <td>{{ config }}</td>
    </tr>
```

In Flask, every template always gets the Flask config passed to it as the `config` variable. In the normal execution of this template, this value gets overwritten in the function below, but since we're calling it and bypassing this function altogether, it doesn't get overwritten. Would this variable not be named config and named `configuration` or `Config` instead, then this exploit wouldn't work. The likelihood of this occurring is so small, but it seems to have happened here.

- https://github.com/pyload/pyload/blob/57d81930edb59177c60830ad8ac36a91d0ec4c4e/src/pyload/webui/app/blueprints/app_blueprint.py#L450C1-L461C51
```python
    context = {
        "python": sys.version,
        "os": " ".join((os.name, sys.platform) + extra),
        "version": api.get_server_version(),
        "folder": PKGDIR,
        "config": api.get_userdir(),
        "download": conf["general"]["storage_folder"]["value"],
        "freespace": format.size(api.free_space()),
        "webif": conf["webui"]["port"]["value"],
        "language": conf["general"]["language"]["value"],
    }
    return render_template("info.html", **context)
 ```

### Impact
Depending on the how the Flask config data is used, it could have detrimental consequences for the security. It's crucial to keep the `SECRET_KEY` secret and never expose it in your code or configuration files.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-mqpq-2p68-46fv
- https://nvd.nist.gov/vuln/detail/CVE-2024-21644
- https://github.com/pyload/pyload/commit/bb22063a875ffeca357aaf6e2edcd09705688c40
- https://github.com/pyload/pyload
