# [M] Arbitrary file write in mindsdb when Extracting Tarballs retrieved from a remote location 

## Summary
Severity: Medium
Advisory: GHSA-7x45-phmr-9wqp
CVE: CVE-2022-23522
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-7x45-phmr-9wqp
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=0 <22.11.4.3

## Details
### Summary

An unsafe extraction is being performed using `shutil.unpack_archive()` from a remotely retrieved tarball. Which may lead to the writing of the extracted files to an unintended location. This vulnerability is sometimes called a **TarSlip** or a **ZipSlip variant**.

### Details

Unpacking files using the high-level function `shutil.unpack_archive()` from a potentially malicious tarball without validating that the destination file path remained within the intended destination directory may cause files to be overwritten outside the destination directory.

As can be seen in the vulnerable snippet code source, an archive is being retrieved using the `download_file()` function from a remote location which is a user-provided permanent storage bucket `s3`. Immediately after being retrieved, the tarball is unsafely unpacked using the function `shutil.unpack_archive()`.

The vulnerable code is [L128..L129](https://github.com/mindsdb/mindsdb/blob/69c76e727b8067f32b06ab83bb835a8c416c4f21/mindsdb/interfaces/storage/fs.py#L128..L129) in [fs.py](https://github.com/mindsdb/mindsdb/blob/69c76e727b8067f32b06ab83bb835a8c416c4f21/mindsdb/interfaces/storage/fs.py) file.

```python3
    def __init__(self):
        super().__init__()
        if 's3_credentials' in self.config['permanent_storage']:
            self.s3 = boto3.client('s3', **self.config['permanent_storage']['s3_credentials'])
        else:
            self.s3 = boto3.client('s3')
       
        # User provided remote storage!
        self.bucket = self.config['permanent_storage']['bucket'] 

    def get(self, local_name, base_dir):
        remote_name = local_name
        remote_ziped_name = f'{remote_name}.tar.gz'
        local_ziped_name = f'{local_name}.tar.gz'
        local_ziped_path = os.path.join(base_dir, local_ziped_name)
        os.makedirs(base_dir, exist_ok=True)
        
        # Retrieve a potentially malicious tarball
        self.s3.download_file(self.bucket, remote_ziped_name, local_ziped_path)

        # Perform an unsafe extraction
        shutil.unpack_archive(local_ziped_path, base_dir)

        os.system(f'chmod -R 777 {base_dir}')
        os.remove(local_ziped_path)
```  

### PoC

The following PoC is provided for illustration purposes only. It showcases the risk of extracting a non-harmless text file `sim4n6.txt` to one of the parent locations rather than the intended current folder.

```bash
> tar --list -f archive.tar
tar: Removing leading "../../../" from member names
../../../sim4n6.txt

> python3 
Python 3.10.6 (main, Nov  2 2022, 18:53:38) [GCC 11.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import shutil
>>> shutil.unpack_archive("archive.tar")
>>> exit()

> test -f ../../../sim4n6.txt && echo "sim4n6.txt exists"
sim4n6.txt exists
```

### Attack Scenario

An attacker could craft a malicious tarball with a filename path, such as `../../../../../../../../etc/passwd`, and then serve the archive remotely using a personal bucket `s3`, thus, retrieve the tarball through **mindsdb** and overwrite the system files of the hosting server. 

### Mitigation

Potential mitigation could be to:
 - Use a safer module, like `zipfile`.
 -  Validate the location of the extracted files and discard those with malicious paths such as relative path `..` or absolute path such as `/etc/password`.
 -  Perform a checksum verification for the retrieved archive, but hard-coding the hashes may be cumbersome and difficult to manage.

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-7x45-phmr-9wqp
- https://nvd.nist.gov/vuln/detail/CVE-2022-23522
- https://github.com/mindsdb/mindsdb
- https://github.com/mindsdb/mindsdb/blob/69c76e727b8067f32b06ab83bb835a8c416c4f21/mindsdb/interfaces/storage/fs.py
- https://github.com/mindsdb/mindsdb/blob/69c76e727b8067f32b06ab83bb835a8c416c4f21/mindsdb/interfaces/storage/fs.py#L128..L129
- https://github.com/mindsdb/mindsdb/releases/tag/v22.11.4.3
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2023-26.yaml
