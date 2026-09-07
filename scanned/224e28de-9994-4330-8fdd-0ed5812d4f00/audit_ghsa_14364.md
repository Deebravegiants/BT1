# [H] Directory traversal + file write causing arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-9p5f-5x8v-x65m
CVE: CVE-2023-30626
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-9p5f-5x8v-x65m
Type: github-advisory

## Affected
- NuGet: `Jellyfin.Controller` — affected >=10.8.0 <10.8.10

## Details
### Impact
Frederic Linn (@FredericLinn) has reported a series of vulnerabilities that can result in directory traversal, file write, and potential remote code execution on Jellyfin instances. The general process involves chaining several exploits including a stored XSS vulnerability and can be used by an unprivileged user.

The general process is (using the example of setting an intro video as the payload):

* Create a session as a low-priviledged user with a crafted authorization header
* Upload an executable that contains a malicious plugin inline via /ClientLog/Document
* (Admin hovers over our device in dashboard -> XSS payload gets triggered)
* XSS Payload tries to set encoder path to our uploaded "log" file via /System/MediaEncoder/Path
* The request fails, but in the process our executable actually runs (I guess for verifying if the path points to a valid ffmpeg version)
* The executable will create a plugin folder and place the inlined plugin DLL inside it
* The XSS payload shuts down the server via /System/Shutdown (separate CVE in `jellyfin-web`)
* After (manually) starting the server, the plugin gets loaded and will:
    * write a new video into the Jellyfin temp folder and register it
    * register this video as the new intro
    * and finally provide a malicious endpoint that simply executes system commands and sends back the results

The ability to write arbitrary content to log files was added in #5918 to allow flexibility to client logging.

The following two sections detail Frederic's exact determinations regarding the two vulnerabilities.

#### Directory traversal and file write

I've been reading the codebase here and there for a couple of days and found a directory traversal inside the ClientLogController, specifically /ClientLog/Document.

The GetRequestInformation method retrieves the name and version of the client from the HttpContext.User object.

Those values are attacker controlled when authenticating against the API. Both values are interpolated into a string, which ultimately ends up as an argument to Path.Combine().

Setting a client name to the relative path "\..\..\..\..\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\test" will write a file with completely attacker controlled content to the executing user's autostart directory.

However, because the attacker only partially controls the filename, exploitation proves to be tricky. That's because the resulting file will always end in ".log", which means putting something in the autostart directory is only going to open notepad on startup. I mean, we can at least insult the user :^).

Anyway, the next logical step would be to write into Jellyfin's plugins directory, but the sub-directories there (of which the already existing configurations directory conveniently counts as one!) are only getting scanned for ".dll" files.

This stops an attacker from providing malicious DLLs that implement the correct interfaces in order to be recognized as legitimate plugins.

On Linux, there might be more options. Running as the standard root user inside a container, an attacker could of course write anywhere. There's the very interesting "/etc/cron.d" directory, where an attacker can place cron jobs that get picked up automatically. Those files, however, can't contain a dot. Moreover, inside the container the cronjobs are probably not being executed, as the Jellyfin process should be only one running.

For the stored XSS component, see https://github.com/jellyfin/jellyfin-web/security/advisories/GHSA-89hp-h43h-r5pq

### Patches
10.8.10

### Workarounds
N/A

### References

A complete write-up is available here: https://gebir.ge/blog/peanut-butter-jellyfin-time/

## References
- https://github.com/jellyfin/jellyfin-web/security/advisories/GHSA-89hp-h43h-r5pq
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-9p5f-5x8v-x65m
- https://nvd.nist.gov/vuln/detail/CVE-2023-30626
- https://github.com/jellyfin/jellyfin/pull/5918
- https://github.com/jellyfin/jellyfin/commit/82ad2633fdfb1c37a158057c7935f83e1129eda7
- https://github.com/jellyfin/jellyfin
- https://github.com/jellyfin/jellyfin/blob/22d880662283980dec994cd7d35fe269613bfce3/Jellyfin.Api/Controllers/ClientLogController.cs#L44
- https://github.com/jellyfin/jellyfin/releases/tag/v10.8.10
