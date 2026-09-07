# [H] Cross-site Scripting Vulnerability on Avatar Upload

## Summary
Severity: High
Advisory: GHSA-q68h-xwq5-mm7x
CVE: CVE-2023-47115
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-q68h-xwq5-mm7x
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.9.2

## Details
# Introduction

This write-up describes a vulnerability found in [Label Studio](https://github.com/HumanSignal/label-studio), a popular open source data labeling tool. The vulnerability affects all versions of Label Studio prior to `1.9.2` and was tested on version `1.8.2`.

# Overview

[Label Studio](https://github.com/HumanSignal/label-studio) has a cross-site scripting (XSS) vulnerability that could be exploited when an authenticated user uploads a crafted image file for their avatar that gets rendered as a HTML file on the website.

# Description

The following [code snippet in Label Studio](https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/users/functions.py#L18-L49) shows that the only verification check is that the file is an image by extracting the dimensions from the file.

```python

def hash_upload(instance, filename):
    filename = str(uuid.uuid4())[0:8] + '-' + filename
    return settings.AVATAR_PATH + '/' + filename <3>


def check_avatar(files):
    images = list(files.items())
    if not images:
        return None

    filename, avatar = list(files.items())[0]  # get first file
    w, h = get_image_dimensions(avatar) <1>
    if not w or not h:
        raise forms.ValidationError("Can't read image, try another one")

    # validate dimensions
    max_width = max_height = 1200
    if w > max_width or h > max_height:
        raise forms.ValidationError('Please use an image that is %s x %s pixels or smaller.'
                                    % (max_width, max_height))

    # validate content type
    main, sub = avatar.content_type.split('/') <2>
    if not (main == 'image' and sub.lower() in ['jpeg', 'jpg', 'gif', 'png']):
        raise forms.ValidationError(u'Please use a JPEG, GIF or PNG image.')

    # validate file size
    max_size = 1024 * 1024
    if len(avatar) > max_size:
        raise forms.ValidationError('Avatar file size may not exceed ' + str(max_size/1024) + ' kb')

    return avatar
```
1. Attempts to get image dimensions to validate the uploaded avatar file is an image.
2. Extracts the `Content-Type` from the upload `POST` request. A user can easily bypass this verification by changing the mimetype of the uploaded file to an allowed type (eg. `image/jpeg`).
3. The file extension of the uploaded file is never validated and is saved to the filesystem.

[Label Studio serves avatar images using Django's built-in `serve` view](https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/users/urls.py#L25-L26), which is [not secure for production use according to Django's documentation](https://docs.djangoproject.com/en/4.2/ref/views/#serving-files-in-development).

```python
    re_path(r'^data/' + settings.AVATAR_PATH + '/(?P<path>.*)$', serve,
            kwargs={'document_root': join(settings.MEDIA_ROOT, settings.AVATAR_PATH)}),
```

The issue with the Django `serve` view is that it determines the `Content-Type` of the response by the file extension in the URL path. Therefore, an attacker can upload an image that contains malicious HTML code and name the file with a `.html` extension to be rendered as a HTML page. The only file extension validation is performed on the client-side, which can be easily bypassed.

# Proof of Concept

Below are the steps to reproduce this issue and execute JavaScript code in the context of the Label Studio website.

1. Using any JPEG or PNG image, add in the comment field in the metadata the HTML code `<script>alert(document.domain)</script>`. This can be done using the `exiftool` command as shown below that was used to create the following image.

```bash
exiftool -Comment='<script>alert(document.domain)</script>' penguin.jpg
```

![xss-penguin](https://user-images.githubusercontent.com/139727151/266989884-c2cd9b4f-f374-416e-a468-acf41f52e088.jpg)

2. On Label Studio, navigate to account & settings page and intercept the upload request of the avatar image using a tool such as Burp Suite. Modify the filename in the request to have a `.html` extension.

3. Right click the image on the avatar profile and copy the URL. Send this to a victim and it will display an alert box with the host name of the Label Studio instance as shown below.

![xss-alert](https://user-images.githubusercontent.com/139727151/266989952-6fb74c6e-9961-447c-a602-5a6f36627ae6.png)

# Impact

Executing arbitrary JavaScript could result in an attacker performing malicious actions on Label Studio users if they visit the crafted avatar image. For an example, an attacker can craft a JavaScript payload that adds a new Django Super Administrator user if a Django administrator visits the image.

# Remediation Advice

* Validate the file extension on the server side, not in client-side code.
* Remove the use of Django's `serve` view and implement a secure controller for viewing uploaded avatar images.
* Consider saving file content in the database rather than on the filesystem to mitigate against other file related vulnerabilities.
* Avoid trusting user controlled inputs.

# Discovered
- August 2023, Alex Brown, elttam

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-q68h-xwq5-mm7x
- https://nvd.nist.gov/vuln/detail/CVE-2023-47115
- https://github.com/HumanSignal/label-studio/commit/a7a71e594f32ec4af8f3f800d5ccb8662e275da3
- https://docs.djangoproject.com/en/4.2/ref/views/#serving-files-in-development
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/users/functions.py#L18-L49
- https://github.com/HumanSignal/label-studio/blob/1.8.2/label_studio/users/urls.py#L25-L26
- https://github.com/pypa/advisory-database/tree/main/vulns/label-studio/PYSEC-2024-126.yaml
