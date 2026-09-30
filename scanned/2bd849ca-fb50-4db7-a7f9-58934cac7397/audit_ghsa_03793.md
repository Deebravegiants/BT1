# [M] Invenio-App vulnerable to host header injection attack

## Summary
Severity: Medium
Advisory: GHSA-94mf-xfg5-r247
CVE: CVE-2019-1020006
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-94mf-xfg5-r247
Type: github-advisory

## Affected
- PyPI: `invenio-app` — affected >=0 <1.0.6
- PyPI: `invenio-app` — affected >=1.1.0 <1.1.1

## Details
## APP_ALLOWED_HOSTS not always preventing host header injection

### Impact
A possible host header injection attack have been identified in Invenio-App.  For an attack to be possible, all conditions below must be met:

1. Your webserver must have been configured to route all requests to your application. 
2. You must have relied on ``APP_ALLOWED_HOSTS`` configuration variable to whitelist allowed host headers.
3. Flask's ``request.host`` must not have been evaluated during request handling.

An example of a view which does not evalute ``request.host`` is a simple view using just ``url_for`` to generate an external URL (similar is possible when rendering just a Jinja template):

```python
@app.route('/')
def index():
    return url_for('index_url', _external=True)
```

This happens, because Werkzeug's trusted host feature, which ``APP_ALLOWED_HOSTS`` rely on, does not check the the list of trusted hosts in it's routing system that ``url_for`` is relying on.

### Patches
Invenio-App v1.0.6 and v1.1.1 fully fix the issue. 

Note, we strongly recommend (see [Securing your instance](https://invenio.readthedocs.io/en/latest/deployment/securing-your-instance.html#allowed-hosts)) that you never route requests to your application with a wrong host header.  The ``APP_ALLOWED_HOSTS`` configuration variable exists as an extra protective measure because it is easy to misconfigure your web server to allow requests with any host header. 

### Workaround 1 - Configure your webserver

You should ensure that you never route requests with a wrong host header to your application. The workaround depends on which web server you are using to proxy requests to your application. In general it involves ensuring that the web server has two virtual hosts defined:

1. **Default virtual host**: a dummy default virtual host that by default is used unless the webserver can match the host header to another virtual host (i.e. a catch-all).
2. **Application virtual host**: the application virtual host responsible for proxing requests to the application, and configured to only reply to a whitelist of host headers.

Note, for instance in Nginx if you only configure the application virtual host, by default, it will also act as the default virtual host despite you having configured a whitelist of host headers.

Below is an example for Nginx. Note for clarity we have only included the virtual host for port 443, but this also extends to virtual hosts running on any other port.
```
# etc/nginx/nginx.conf
http {
  # ...
  include /etc/nginx/conf.d/*.conf;
}
```

**Default virtual host**

Notice, the ``server_name`` is ``_`` and the ``listen`` directive has it marked as ``default_server``.

```
# etc/nginx/conf.d/default.conf
server {
  listen 443 default_server;
  listen [::]:443 default_server;
  server_name _;

  # ... 

  return 301 https://www.example.com;
}
```

**Application virtual host**

Notice, the ``server_name`` is set to the host header whitelist.

```
# etc/nginx/conf.d/app.conf
server {
  listen 443;
  listen [::]:443;
  server_name www.example.com;

  # ...
}
```

### Workaround 2 - Include application snippet

We strongly recommend that you use the method described in Workaround 1.

If you are not able to upgrade to the patched versions of Invenio-App, you can include the following code snippet in your application to force evaluation of ``request.hosts``.

```python
@app.before_request
def before_request():
    request.host
```

### For more information
If you have any questions or comments about this advisory:
* Email us at [info@inveniosoftware.org](mailto:info@inveniosoftware.org)

## References
- https://github.com/inveniosoftware/invenio-app/security/advisories/GHSA-94mf-xfg5-r247
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020006
- https://github.com/advisories/GHSA-94mf-xfg5-r247
- https://github.com/inveniosoftware/invenio-app
- https://github.com/pypa/advisory-database/tree/main/vulns/invenio-app/PYSEC-2019-24.yaml
