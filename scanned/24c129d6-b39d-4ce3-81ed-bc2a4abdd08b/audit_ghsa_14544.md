# [H] mindsdb arbitrary file write when extracting a remotely retrieved Tarball

## Summary
Severity: High
Advisory: GHSA-2g5w-29q9-w6hx
CVE: CVE-2023-30620
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-2g5w-29q9-w6hx
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=0 <23.2.1.0

## Details
### Summary

An unsafe extraction is being performed using `tarfile.extractall()` from a remotely retrieved tarball. Which may lead to the writing of the extracted files to an unintended location. Sometimes, the vulnerability is called a TarSlip or a ZipSlip variant.

### Details

I commented the following snippet of code as a vulnerability details. The code is from [file.py#L26..L134](https://github.com/mindsdb/mindsdb/blob/afedd37c16e579b6dc075b0814e42d0505ccdc07/mindsdb/api/http/namespaces/file.py#L26..L134)

```python
@ns_conf.route('/<name>')
@ns_conf.param('name', "MindsDB's name for file")
class File(Resource):
    @ns_conf.doc('put_file')
    def put(self, name: str):
        ''' add new file
            params in FormData:
                - file
                - original_file_name [optional]
        '''

        data = {}

        ... omitted for brevity

            url = data['source']
            data['file'] = data['name']

            ... omitted for brevity 

            with requests.get(url, stream=True) as r:                   # Source: retrieve the URL which point to a remotely located tarball 
                if r.status_code != 200:
                    return http_error(
                        400,
                        "Error getting file",
                        f"Got status code: {r.status_code}"
                    )
                file_path = os.path.join(temp_dir_path, data['file'])
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):   # write with chunks the remote retrieved file into file_path location 
                        f.write(chunk)

        original_file_name = data.get('original_file_name')

        file_path = os.path.join(temp_dir_path, data['file'])      
        lp = file_path.lower()
        if lp.endswith(('.zip', '.tar.gz')):
            if lp.endswith('.zip'):
                with zipfile.ZipFile(file_path) as f:
                    f.extractall(temp_dir_path)
            elif lp.endswith('.tar.gz'):
                with tarfile.open(file_path) as f:  # Just after 
                    f.extractall(temp_dir_path)  # Sink: the tarball located by file_path is supposed to be extracted to temp_dir_path. 
```

So, a remotely available tarball is being retrieved and written to the server filesystem in chunks, and then, if the extension ends with `.tar.gz` of a compressed tarball, the mindsdb app applies `tarfile.extractall()` directly with no checks for the destination. 

However, according to the following [warning](https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractall) from the official documentation;

> Warning: Never extract archives from untrusted sources without prior inspection. It is possible that files are created outside of path, e.g. members that have absolute filenames starting with "/" or filenames with two dots "..". 


### PoC

The following PoC is provided for illustration purposes only. It showcases the risk of extracting a non-harmless text file `sim4n6.txt` to one of the parent locations rather than the intended current folder.

```bash
> tar --list -v -f archive.tar.gz
tar: Removing leading "../../../" from member names
../../../sim4n6.txt

> python3 
Python 3.10.6 (main, Nov  2 2022, 18:53:38) [GCC 11.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import tarfile
>>> with tarfile.open("archive.tar.gz") as tf:
>>>         tf.extractall()
>>> exit()

> test -f ../../../sim4n6.txt && echo "sim4n6.txt exists"
sim4n6.txt exists
```

### Attack Scenario

An attacker could craft a malicious tarball with a filename path, such as ../../../../../../../../etc/passwd, and then serve the archive remotely, proceed to the PUT request of the tarball through mindsdb and overwrite the system files of the hosting server for instance.

### Mitigation 

Potential mitigation could be to:
 - Use a safer module, like `zipfile`.
 - Use an alternative of `tarfile`, such as `tarsafe`. 
  - Validate the location or the absolute path of the extracted files and discard those with malicious paths such as relative path `../../..` or absolute path such as `/etc/password`. A simple wrapper could be written to raise an exception when a path traversal may be identified.

This is similar to the other report [GHSA-7x45-phmr-9wqp](https://github.com/mindsdb/mindsdb/security/advisories/GHSA-7x45-phmr-9wqp).

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-2g5w-29q9-w6hx
- https://nvd.nist.gov/vuln/detail/CVE-2023-30620
- https://github.com/mindsdb/mindsdb/commit/4419b0f0019c000db390b54d8b9d06e1d3670039
- https://github.com/mindsdb/mindsdb
- https://github.com/mindsdb/mindsdb/blob/afedd37c16e579b6dc075b0814e42d0505ccdc07/mindsdb/api/http/namespaces/file.py#L26..L134
- https://github.com/mindsdb/mindsdb/releases/tag/v23.2.1.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2023-27.yaml
