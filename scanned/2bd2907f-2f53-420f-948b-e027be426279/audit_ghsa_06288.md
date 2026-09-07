# [M] reachy_mini Allows Unrestricted Upload of File with Dangerous Type

## Summary
Severity: Medium
Advisory: GHSA-m2pc-3q4q-w6jr
CVE: CVE-2026-55419
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-m2pc-3q4q-w6jr
Type: github-advisory

## Affected
- PyPI: `reachy-mini` — affected >=0 <1.8.2

## Details
## Summary

The Reachy Mini daemon exposes the “/api/media/sounds/upload” endpoint without authentication and file validation mechanisms.  
An attacker can use this endpoint to upload malicious files into the file system that will propagate in future attacks.

## Compromise Chain: Unauthenticated to Full Root Access

This issue is part of a full compromise chain allowing an unauthenticated user to gain root access on the Reachy’s operating system:

1. Unrestricted File Upload in Media Sounds Upload API \<= current finding  
2. Bluetooth Authentication Bypass  
3. Bluetooth Directory Traversal


## Description

The root cause of the issue is at the handler located in “***src/daemon/app/routers/media.py***” file at the “upload\_sound” method:

```py
@router.post("/sounds/upload")
async def upload_sound(
    file: UploadFile = File(...),
) -> dict[str, str]:
    """Upload a sound file to the daemon's temporary sound directory.
    The file is saved to ``/tmp/reachy_mini_sounds/<original_filename>``.
    If a file with the same name already exists it is overwritten.
    Returns:
        JSON with the absolute *path* of the saved file on the daemon.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    # Reject path traversal
    filename = Path(file.filename).name
    if not filename or filename in (".", ".."):
        raise HTTPException(status_code=400, detail="Invalid filename")
    os.makedirs(SOUNDS_TMP_DIR, exist_ok=True)
    dest = os.path.join(SOUNDS_TMP_DIR, filename)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    return {"status": "ok", "path": dest}
```

This endpoint lacks multiple defence mechanisms:

1. No authentication mechanism.  
2. No file extension validation.  
3. No file content/size validation.

Additionally, the daemon is bound to the 0.0.0.0 network interfaces (a.k.a. all network interfaces) by default along with permissive CORS ( allow\_origins=\[“\*”\] ) meaning the following API endpoint is exposed to every network interface the daemon is connected to.

# PoC

1. Start the daemon in simulation mode (command depends on the installed environment):

```shell
 .venv/bin/mjpython -m reachy_mini.daemon.app.main --sim --no-media
```

2. After that check that the media upload API endpoint is activated and you can upload a wav file:

```shell
curl -X POST http://<daemon_domain>:<daemon_port>/api/media/sounds/upload \
    -F "file=@/path/to/your/file.wav"
```

3. Now attempt to create a “.sh” file containing a script and upload it:

```shell
curl -X POST http://<daemon_domain>:<daemon_port>/api/media/sounds/upload \
    -F "file=@/path/to/your/script.sh"
```

4. Now error message will be received and you will see that the script file was successfully uploaded to disk.

# Impact

Due to this issue, an attacker can upload malicious files instead of the intended sounds files, harming the integrity of the stored data and allowing an attacker to propagate a foothold in cases another vulnerabilities would arise.

## Fix suggestion

Perform the following check on the API endpoint:

1. Validate that the file extension contains only desired extensions (allow-list approach).  
2. Validate that the uploaded file’s content matches the desired extension (Magic numbers, and known file structure per file type).  
3. Enforce authentication on the file upload endpoint.

## Credit

The vulnerability was discovered by Natan Nehorai of the JFrog Vulnerability Research team.

## References
- https://github.com/pollen-robotics/reachy_mini/security/advisories/GHSA-m2pc-3q4q-w6jr
- https://github.com/pollen-robotics/reachy_mini/commit/984c7723b3ec5da63f4e0a2bcf9f120ceb563e04
- https://github.com/pollen-robotics/reachy_mini
